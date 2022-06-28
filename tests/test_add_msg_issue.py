import pytest

from add_msg_issue_hook.add_msg_issue import insert_issue_into_message

TEMPLATE: str = "{subject}\n\n[{issue_id}]\n{body}"


@pytest.mark.parametrize(
    "message_in, message_out",
    [
        # Single text line
        (("Subject line."), ("Subject line.\n" "\n" "[{issue_id}]")),
        # 2 text lines, no linebreak
        (
            ("Subject line.\n" "Body line 1"),
            ("Subject line.\n" "\n" "[{issue_id}]\n" "Body line 1"),
        ),
        # 2 text lines, with linebreak
        (
            ("Subject line.\n" "\n" "Body line 1"),
            ("Subject line.\n" "\n" "[{issue_id}]\n" "Body line 1"),
        ),
        # Subject line and longer body
        (
            ("Subject line.\n" "\n" "Body line 1\n" "Body line 2"),
            ("Subject line.\n" "\n" "[{issue_id}]\n" "Body line 1\n" "Body line 2"),
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
        (("# some comment"), ("[{issue_id}]\n" "# some comment")),
        (
            ("# some comment \n" "\n" "# some other comment\n" "# A third comment."),
            (
                "[{issue_id}]\n"
                "# some comment \n"
                "\n"
                "# some other comment\n"
                "# A third comment."
            ),
        ),
    ],
)
class TestInsertIssueIntoMessage:
    @staticmethod
    @pytest.mark.parametrize("issue_id", ["TESTID-12345"])
    def test_with_issue_id(message_in, message_out, issue_id):

        outstr = insert_issue_into_message(issue_id, message_in, TEMPLATE)

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
