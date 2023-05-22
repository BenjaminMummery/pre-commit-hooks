# Copyright (c) 2023 Benjamin Mummery


from unittest.mock import Mock

import pytest

from src.add_msg_issue_hook import add_msg_issue

from ..conftest import ADD_MSG_ISSUE_FIXTURE_LIST as FIXTURES

DEFAULT_TEMPLATE = "{subject}\n\n[{issue_id}]\n{body}"
FALLBACK_TEMPLATE = "{message}\n[{issue_id}]"


@pytest.mark.usefixtures(*[f for f in FIXTURES if f != "mock_get_branch_name"])
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


@pytest.mark.usefixtures(
    *[f for f in FIXTURES if f != "mock_get_issue_ids_from_branch_name"]
)
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


@pytest.mark.usefixtures(*[f for f in FIXTURES if f != "mock_issue_is_in_message"])
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


@pytest.mark.usefixtures(
    *[f for f in FIXTURES if f != "mock_insert_issue_into_message"]
)
class TestInsertIssueIntoMessage:
    @staticmethod
    @pytest.mark.parametrize(
        "message",
        [
            "# <message sentinel>",
            "# <comment line sentinel>\n<body line 1 sentinel>\n<body line 2 sentinel>",
        ],
    )
    def test_uses_fallback_template_if_message_has_no_subject(
        message, mock_fallback_template
    ):
        # WHEN
        p = add_msg_issue._insert_issue_into_message(
            "<issue ID sentinel>", message, "<template sentinel>"
        )

        # THEN
        mock_fallback_template.format.assert_called_once_with(
            issue_id="<issue ID sentinel>", message=message
        )
        assert p == mock_fallback_template.format().strip()

    @staticmethod
    @pytest.mark.parametrize(
        "message, subject, body",
        [
            (
                "<subject sentinel>\n<body sentinel>",
                "<subject sentinel>",
                "<body sentinel>",
            ),
        ],
    )
    def test_uses_full_template_if_possible(message, subject, body):
        assert (
            add_msg_issue._insert_issue_into_message(
                "<issue ID sentinel>",
                message,
                "<template sentinel> {body}-{issue_id}-{subject}",
            )
            == "<template sentinel> " + body + "-<issue ID sentinel>-" + subject
        )

    @staticmethod
    @pytest.mark.parametrize(
        "message, subject, body",
        [
            (
                "<subject sentinel>\n# <body sentinel>",
                "<subject sentinel>",
                "# <body sentinel>",
            ),
        ],
    )
    def test_handles_body_comment_lines(message, subject, body):
        # WHEN
        out = add_msg_issue._insert_issue_into_message(
            "<issue ID sentinel>",
            message,
            "<template sentinel> {body}-{issue_id}-{subject}",
        )

        # THEN
        expected = "<template sentinel> \n" + body + "-<issue ID sentinel>-" + subject
        assert out == expected, f"\nout = {out}\nexp = {expected}"


@pytest.mark.usefixtures(
    *[
        f
        for f in FIXTURES
        if f
        not in [
            "mock_parse_add_msg_issue_args",
            "mock_default_template",
            "mock_fallback_template",
        ]
    ]
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


@pytest.mark.usefixtures(*FIXTURES)
class TestMain:
    @staticmethod
    def test_early_return_for_no_issue_id(mock_get_issue_ids_from_branch_name):
        mock_get_issue_ids_from_branch_name.return_value = []
        assert add_msg_issue.main() is None

    @staticmethod
    def test_early_return_for_issue_already_in_message(
        mock_issue_is_in_message,
        tmp_path,
        mock_parse_add_msg_issue_args,
        mock_get_issue_ids_from_branch_name,
        mock_insert_issue_into_message,
    ):
        # GIVEN
        f = tmp_path / "stub_file"
        f.write_text("<file contents sentinel>")
        mock_get_issue_ids_from_branch_name.return_value = ["<issue sentinel>"]
        mock_issue_is_in_message.return_value = True
        mock_parse_add_msg_issue_args.return_value = Mock(commit_msg_filepath=f)

        # WHEN
        assert add_msg_issue.main() is None

        # THEN
        mock_get_issue_ids_from_branch_name.assert_called_once()
        mock_issue_is_in_message.assert_called_once_with(
            "<issue sentinel>", "<file contents sentinel>"
        )
        with open(f) as file:
            content = file.read()
        assert content == "<file contents sentinel>"
        mock_insert_issue_into_message.assert_not_called()

    @staticmethod
    def test_rewrites_file_contents(
        mock_issue_is_in_message,
        tmp_path,
        mock_parse_add_msg_issue_args,
        mock_get_issue_ids_from_branch_name,
        mock_insert_issue_into_message,
    ):
        # GIVEN
        f = tmp_path / "stub_file"
        f.write_text("<file contents sentinel>")
        mock_get_issue_ids_from_branch_name.return_value = ["<issue sentinel>"]
        mock_issue_is_in_message.return_value = False
        mock_parse_add_msg_issue_args.return_value = Mock(
            commit_msg_filepath=f, template="<template sentinel>"
        )
        mock_insert_issue_into_message.return_value = "<new contents sentinel>"

        # WHEN
        assert add_msg_issue.main() is None

        # THEN
        mock_get_issue_ids_from_branch_name.assert_called_once()
        mock_issue_is_in_message.assert_called_once_with(
            "<issue sentinel>", "<file contents sentinel>"
        )
        with open(f) as file:
            content = file.read()
        assert content == "<new contents sentinel>"
        mock_insert_issue_into_message.assert_called_once_with(
            "<issue sentinel>", "<file contents sentinel>", "<template sentinel>"
        )
