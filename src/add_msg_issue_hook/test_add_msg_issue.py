# Copyright (c) 2024 Benjamin Mummery

from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from src.add_msg_issue_hook import add_msg_issue
from src.add_msg_issue_hook.add_msg_issue import BranchNameReadError, subprocess


class TestGetBranchName:
    @staticmethod
    def test_failure_states(mocker: MockerFixture):
        # GIVEN
        mocker.patch(
            f"{add_msg_issue.__name__}.subprocess.check_output",
            Mock(side_effect=subprocess.CalledProcessError(0, "<cmd sentinel>")),
        )

        # WHEN
        with pytest.raises(BranchNameReadError) as e:
            _ = add_msg_issue._get_branch_name()

        # THEN
        assert (
            "Getting branch name for add_msg_issue_hook pre-commit hook failed."
            in e.exconly()
        )

    @staticmethod
    def test_returns_branch_name(mocker: MockerFixture):
        # GIVEN
        mocker.patch(
            f"{add_msg_issue.__name__}.subprocess.check_output",
            Mock(return_value="<branch name sentinel>"),
        )

        # WHEN
        ret = add_msg_issue._get_branch_name()

        # THEN
        assert ret == "<branch name sentinel>"

    @staticmethod
    def test_strips_whitespace(mocker: MockerFixture):
        # GIVEN
        mocker.patch(
            f"{add_msg_issue.__name__}.subprocess.check_output",
            Mock(return_value="   <branch name sentinel>   "),
        )

        # WHEN
        ret = add_msg_issue._get_branch_name()

        # THEN
        assert ret == "<branch name sentinel>"


class TestGetIssueIDsFromBranchName:
    @staticmethod
    @pytest.mark.parametrize("input, expected", [("sdk-1123/do/something", "SDK-1123")])
    def test_extracts_single_issue_id(input, expected):
        assert add_msg_issue._get_issue_ids_from_branch_name(input) == [expected]

    @staticmethod
    @pytest.mark.parametrize("input", ["do/something"])
    def test_returns_empty_list_for_no_issue_ids(input):
        assert add_msg_issue._get_issue_ids_from_branch_name(input) == []

    @staticmethod
    @pytest.mark.parametrize(
        "input, expected", [("sdk-1123/op-2187/do/something", ["SDK-1123", "OP-2187"])]
    )
    def test_returns_multiple_ids(input, expected):
        assert add_msg_issue._get_issue_ids_from_branch_name(input) == expected


class TestIssueIsInMessage:
    @staticmethod
    def test_returns_true_if_issue_already_in_message_single_line():
        # GIVEN
        issue = "SDK-1123"
        message = "did something (SDK-1123)"

        # WHEN
        ret = add_msg_issue._issue_is_in_message(issue, message)

        # THEN
        assert ret

    @staticmethod
    def test_returns_true_if_issue_already_in_message_multiple_lines():
        # GIVEN
        issue = "SDK-1123"
        message = "did something\n\nsdk-1123\n"

        # WHEN
        ret = add_msg_issue._issue_is_in_message(issue, message)

        # THEN
        assert ret

    @staticmethod
    def test_returns_false_if_issue_not_in_message():
        # GIVEN
        issue = "SDK-1123"
        message = "did something\n\nand some details\n"

        # WHEN
        ret = add_msg_issue._issue_is_in_message(issue, message)

        # THEN
        assert not ret


class TestInsertIssueIntoMessage:
    @staticmethod
    def test_early_return_if_message_starts_with_comment():
        # GIVEN
        issue = "SDK-1123"
        message = "# Some comment\n\nNot a comment down here."
        template = Mock()

        # WHEN
        ret = add_msg_issue._insert_issue_into_message(issue, message, template)

        # THEN
        assert ret == f"{message}\n[{issue}]"

    @staticmethod
    def test_handles_trailing_newline_in_message():
        # GIVEN
        issue = "SDK-1123"
        message = "# Some comment\n\nNot a comment down here."
        template = Mock()

        # WHEN
        ret = add_msg_issue._insert_issue_into_message(
            issue, message + "\n\n", template
        )

        # THEN
        assert ret == f"{message}\n[{issue}]"
