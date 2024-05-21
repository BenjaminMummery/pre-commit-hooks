# Copyright (c) 2024 Benjamin Mummery

from unittest.mock import Mock, create_autospec, mock_open

import pytest
from pytest_mock import MockerFixture

from src.add_msg_issue_hook import add_msg_issue
from src.add_msg_issue_hook.add_msg_issue import (
    BranchNameReadError,
    argparse,
    subprocess,
)


class TestGetBranchName:
    @staticmethod
    def test_failure_states(mocker: MockerFixture):
        # GIVEN
        mocker.patch(
            f"{add_msg_issue.__name__}.subprocess.check_output",
            side_effect=subprocess.CalledProcessError(0, "<cmd sentinel>"),
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
            return_value="<branch name sentinel>",
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
            return_value="   <branch name sentinel>   ",
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
    class TestMessageStartsWithComment:
        @staticmethod
        def test_single_line_message():
            # GIVEN
            issue = "<issue sentinel>"
            message = "# <message sentinel>"
            template = Mock()

            # WHEN
            ret = add_msg_issue._insert_issue_into_message(issue, message, template)

            # THEN
            assert ret == f"{message}\n[{issue}]"

        @staticmethod
        def test_multi_line_message():
            # GIVEN
            issue = "<issue sentinel>"
            message = "# <message sentinel>\n\n<message content sentinel>"
            template = Mock()

            # WHEN
            ret = add_msg_issue._insert_issue_into_message(issue, message, template)

            # THEN
            assert ret == f"{message}\n[{issue}]"

        @staticmethod
        def test_handles_trailing_newline_in_message():
            # GIVEN
            issue = "<issue sentinel>"
            message = "# <message sentinel>"
            template = Mock()

            # WHEN
            ret = add_msg_issue._insert_issue_into_message(
                issue, message + "\n\n", template
            )

            # THEN
            assert ret == f"{message}\n[{issue}]"

    class TestMessageStartsWithContent:
        @staticmethod
        def test_subject_only():
            # GIVEN
            issue = "<issue sentinel>"
            message = "<message sentinel>"
            template = "<template sentinel>\n{subject}\n{issue_id}\n{body}"

            # WHEN
            ret = add_msg_issue._insert_issue_into_message(issue, message, template)

            # THEN
            assert ret == "<template sentinel>\n<message sentinel>\n<issue sentinel>"

        @staticmethod
        def test_subject_and_body():
            # GIVEN
            issue = "<issue sentinel>"
            message = "<subject sentinel>\n\n<body sentinel>"
            template = "<template sentinel>\n{subject}\n{issue_id}\n{body}"

            # WHEN
            ret = add_msg_issue._insert_issue_into_message(issue, message, template)

            # THEN
            assert (
                ret
                == "<template sentinel>\n<subject sentinel>\n<issue sentinel>\n<body sentinel>"  # noqa: E501
            )

        @staticmethod
        def test_handles_comment_led_body():
            # GIVEN
            issue = "<issue sentinel>"
            message = "<subject sentinel>\n\n# <body sentinel>"
            template = "<template sentinel>\n{subject}\n{issue_id}\n{body}"

            # WHEN
            ret = add_msg_issue._insert_issue_into_message(issue, message, template)

            # THEN
            assert (
                ret
                == "<template sentinel>\n<subject sentinel>\n<issue sentinel>\n\n# <body sentinel>"  # noqa: E501
            )


class TestParseArgs:
    @staticmethod
    def test_parse_args(mocker: MockerFixture):
        # GIVEN
        mocked_namespace = create_autospec(argparse.Namespace)
        mocked_namespace.template = "{subject}{body}{issue_id}"
        mocked_argparse = create_autospec(argparse.ArgumentParser)
        mocked_argparse.parse_args.return_value = mocked_namespace
        mocker.patch(
            f"{add_msg_issue.__name__}.argparse.ArgumentParser",
            return_value=mocked_argparse,
        )

        # WHEN
        ret = add_msg_issue._parse_args()

        # THEN
        assert ret == mocked_namespace

    @staticmethod
    @pytest.mark.parametrize(
        "template", ["{body}{issue_id}", "{subject}{issue_id}", "{subject}{body}"]
    )
    def test_raises_keyerror_for_missing_template_key(
        mocker: MockerFixture, template: str
    ):
        # GIVEN
        mocked_namespace = create_autospec(argparse.Namespace)
        mocked_namespace.template = template
        mocked_argparse = create_autospec(argparse.ArgumentParser)
        mocked_argparse.parse_args.return_value = mocked_namespace
        mocker.patch(
            f"{add_msg_issue.__name__}.argparse.ArgumentParser",
            return_value=mocked_argparse,
        )

        # WHEN / THEN
        with pytest.raises(KeyError):
            _ = add_msg_issue._parse_args()

    @staticmethod
    def test_raises_keyerror_for_unrecognised_template_key(mocker: MockerFixture):
        # GIVEN
        mocked_namespace = create_autospec(argparse.Namespace)
        mocked_namespace.template = "{subject}{body}{issue_id}{something_else}"
        mocked_argparse = create_autospec(argparse.ArgumentParser)
        mocked_argparse.parse_args.return_value = mocked_namespace
        mocker.patch(
            f"{add_msg_issue.__name__}.argparse.ArgumentParser",
            return_value=mocked_argparse,
        )

        # WHEN / THEN
        with pytest.raises(KeyError):
            _ = add_msg_issue._parse_args()


class TestMain:
    @staticmethod
    def test_handles_detached_HEAD(mocker: MockerFixture):
        # GIVEN
        mocker.patch(
            f"{add_msg_issue.__name__}._parse_args",
        )
        mocker.patch(
            f"{add_msg_issue.__name__}._get_branch_name",
            side_effect=BranchNameReadError,
        )
        mocked_get_issue_ids = mocker.patch(
            f"{add_msg_issue.__name__}._get_issue_ids_from_branch_name",
        )
        mocked_open = mocker.patch("builtins.open")
        mocked_issue_in_message = mocker.patch(
            f"{add_msg_issue.__name__}._issue_is_in_message",
        )

        # WHEN
        ret = add_msg_issue.main()

        # THEN
        assert ret == 0
        mocked_get_issue_ids.assert_not_called()
        mocked_open.assert_not_called()
        mocked_issue_in_message.assert_not_called()

    @staticmethod
    def test_early_return_for_no_issues(mocker: MockerFixture):
        # GIVEN
        mocker.patch(
            f"{add_msg_issue.__name__}._parse_args",
        )
        mocker.patch(f"{add_msg_issue.__name__}._get_branch_name")
        mocker.patch(
            f"{add_msg_issue.__name__}._get_issue_ids_from_branch_name",
            return_value=[],
        )
        mocked_open = mocker.patch("builtins.open")
        mocked_issue_in_message = mocker.patch(
            f"{add_msg_issue.__name__}._issue_is_in_message",
        )

        # WHEN
        ret = add_msg_issue.main()

        # THEN
        assert ret == 0
        mocked_open.assert_not_called()
        mocked_issue_in_message.assert_not_called()

    @staticmethod
    def test_early_return_for_issue_already_in_message(mocker: MockerFixture):
        # GIVEN
        mocker.patch(
            f"{add_msg_issue.__name__}._parse_args",
        )
        mocker.patch(f"{add_msg_issue.__name__}._get_branch_name")
        mocker.patch(
            f"{add_msg_issue.__name__}._get_issue_ids_from_branch_name",
            return_value=["<issue sentinel>"],
        )
        mocker.patch("builtins.open", mock_open(read_data="<message sentinel>"))
        mocker.patch(
            f"{add_msg_issue.__name__}._issue_is_in_message",
            return_value=True,
        )

        # WHEN
        ret = add_msg_issue.main()

        # THEN
        assert ret == 0

    @staticmethod
    def test_write(mocker: MockerFixture):
        # GIVEN
        mocker.patch(
            f"{add_msg_issue.__name__}._parse_args",
        )
        mocker.patch(f"{add_msg_issue.__name__}._get_branch_name")
        mocker.patch(
            f"{add_msg_issue.__name__}._get_issue_ids_from_branch_name",
            return_value=["<issue sentinel>"],
        )
        mocker.patch("builtins.open", mock_open(read_data="<message sentinel>"))
        mocker.patch(
            f"{add_msg_issue.__name__}._issue_is_in_message",
            return_value=False,
        )

        # WHEN
        ret = add_msg_issue.main()

        # THEN
        assert ret == 0
