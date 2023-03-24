# Copyright (c) 2023 Benjamin Mummery


import pytest

from src.add_msg_issue_hook import add_msg_issue

DEFAULT_TEMPLATE = "{subject}\n\n[{issue_id}]\n{body}"
FALLBACK_TEMPLATE = "{message}\n[{issue_id}]"


class TestGetBranchName:
    @staticmethod
    @pytest.mark.parametrize(
        "branch_name", ["test-branch", "feature/TESTID-010/something"]
    )
    def test_gets_branch_name(branch_name, git_repo, cwd):
        git_repo.run(f"git checkout -b {branch_name}")

        with cwd(git_repo.workspace):
            branch = add_msg_issue._get_branch_name()

        assert branch == branch_name, (
            f"_get_branch_name returned '{branch}' when we expected '{branch_name}'.\n"
            "Context:\n"
            f" - Temporary git repo initialised at {git_repo.workspace}\n"
        )

    @staticmethod
    @pytest.mark.parametrize(
        "exception",
        [Exception("exception test string"), ValueError("value error test string")],
    )
    def test_on_exception_prints_exception_and_returns_empty_string(
        exception, mocker, capsys
    ):
        mocker.patch("subprocess.check_output", side_effect=exception)

        branch = add_msg_issue._get_branch_name()

        assert branch == ""
        assert str(exception) in capsys.readouterr().out


class TestGetIssueIDSFromBranch:
    @staticmethod
    @pytest.mark.parametrize(
        "branch_name, issue_ids",
        [
            ("feature/TEAMID-010/something", ["TEAMID-010"]),
            ("feature/something/TEAMID-010", ["TEAMID-010"]),
        ],
    )
    def test_finds_existing_id(branch_name, issue_ids):
        assert add_msg_issue._get_issue_ids_from_branch_name(branch_name) == issue_ids

    @staticmethod
    @pytest.mark.parametrize(
        "branch_name", ["main", "dev", "feature/bmummery/confetti"]
    )
    def test_ignores_nonexistant_ids(branch_name):
        assert add_msg_issue._get_issue_ids_from_branch_name(branch_name) == []


class TestIssueIsInMessage:
    @staticmethod
    @pytest.mark.parametrize(
        "issue_id, message", [("TESTID-010", "fix: TESTID-010: summary")]
    )
    def test_returns_true_if_issue_is_in_message(issue_id, message):
        assert add_msg_issue._issue_is_in_message(issue_id, message)

    @staticmethod
    @pytest.mark.parametrize(
        "issue_id, message", [("TESTID-010", "fix: TESTID-011: summary")]
    )
    def test_returns_false_if_issue_is_not_in_message(issue_id, message):
        assert not add_msg_issue._issue_is_in_message(issue_id, message)

    @staticmethod
    @pytest.mark.parametrize(
        "issue_id, message", [("TESTID-010", "# fix: TESTID-010: summary")]
    )
    def test_returns_false_if_issue_is_only_in_comments(issue_id, message):
        assert not add_msg_issue._issue_is_in_message(issue_id, message)


class TestInsertIssueIntoMessage:
    @staticmethod
    @pytest.mark.parametrize("issue_id", ["TESTID-12345"])
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
    def test_default_template_formats_correctly(message_in, message_out, issue_id):
        outstr = add_msg_issue._insert_issue_into_message(
            issue_id, message_in, DEFAULT_TEMPLATE
        )

        expected_message_out = message_out.format(issue_id=issue_id)
        assert outstr == expected_message_out, (
            "insert_issue_into_message returned an incorrect string.\n"
            "Input string:\n" + "-" * 40 + "\n"
            f"{message_in}\n" + "-" * 40 + "\n"
            "Output string:\n" + "-" * 40 + "\n"
            f"{outstr}\n" + "-" * 40 + "\n"
            "Expected output:\n" + "-" * 40 + "\n"
            f"{expected_message_out}\n" + "-" * 40 + "\n"
        )

    @staticmethod
    @pytest.mark.parametrize("issue_id", ["TESTID-12345"])
    @pytest.mark.parametrize(
        "template, message_in, message_out",
        [
            (
                "{issue_id}: {subject}\n\n{body}",
                "Subject line.\nbody line",
                "{issue_id}: Subject line.\n\nbody line",
            )
        ],
    )
    def test_user_defined_template_formats_correctly(
        issue_id, template, message_in, message_out
    ):
        outstr = add_msg_issue._insert_issue_into_message(
            issue_id, message_in, template
        )

        expected_message_out = message_out.format(issue_id=issue_id)
        assert outstr == expected_message_out, (
            "insert_issue_into_message returned an incorrect string.\n"
            "Input string:\n" + "-" * 40 + "\n"
            f"{message_in}\n" + "-" * 40 + "\n"
            "Output string:\n" + "-" * 40 + "\n"
            f"{outstr}\n" + "-" * 40 + "\n"
            "Expected output:\n" + "-" * 40 + "\n"
            f"{expected_message_out}\n" + "-" * 40 + "\n"
        )


class TestParseArgs:
    class TestParsingCommitMessageFilepath:
        @staticmethod
        @pytest.mark.parametrize("commit_msg_filepath", ["test/path/1", "test_path_2/"])
        def test_interprets_msg_filepath(commit_msg_filepath, mocker):
            mocker.patch("sys.argv", ["stub_name", commit_msg_filepath])

            args = add_msg_issue._parse_args()

            assert args.commit_msg_filepath == commit_msg_filepath

    class TestParsingTemplates:
        valid_templates = ["{issue_id}{subject}{body}"]
        invalid_templates = [
            "no keywords",
            "only {issue_id} keyword",
            "only {subject} keyword",
            "only {body} keyword",
            "{issue_id} and {subject}, no 'body'",
            "{issue_id} and {body}, no 'subject'",
            "{subject} and {body}, no 'issue_id'",
            "has {extra} keyword as well as all required {issue_id}{subject}{body}",
        ]

        @staticmethod
        def test_uses_default_when_no_template_specified(mocker):
            mocker.patch("sys.argv", ["stub_name", "stub_filepath"])

            args = add_msg_issue._parse_args()

            assert args.template == DEFAULT_TEMPLATE

        @staticmethod
        @pytest.mark.parametrize("flag", ["-t", "--template"])
        @pytest.mark.parametrize("template", valid_templates)
        def test_interprets_valid_template(flag, template, mocker):
            mocker.patch("sys.argv", ["stub_name", "stub_filepath", flag, template])

            args = add_msg_issue._parse_args()

            assert args.template == template

        @staticmethod
        @pytest.mark.parametrize("template", invalid_templates)
        def test_uses_default_when_invalid_template_specified(template, mocker):
            mocker.patch("sys.argv", ["stub_name", "stub_filepath", "-t", template])

            args = add_msg_issue._parse_args()

            assert args.template == DEFAULT_TEMPLATE
