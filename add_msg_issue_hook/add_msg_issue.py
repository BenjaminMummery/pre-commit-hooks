#!/usr/bin/env python3

import argparse
import re
import subprocess


def _get_branch_name() -> str:
    branch: str = ""
    try:
        branch = subprocess.check_output(
            ["git", "symbolic-ref", "--short", "HEAD"], universal_newlines=True
        ).strip()
    except Exception as e:
        print("Getting branch name for add_msg_issue_hook pre-commit hook failed:")
        print(e)
    return branch


def _get_issue_ids_from_branch_name(branch: str) -> list:
    """Parse the branch name looking for an issue ID.

    Issue IDs are assumed to follow "X-Y" where X is a string of 1-10 letters, and
    Y is a string of 1-5 numerals.

    Args:
        branch (str): the name of the current branch.

    Returns:
        str: the first instance of something resembling a jira issue id.
    """
    matches = re.findall("[a-zA-Z]{1,10}-[0-9]{1,5}", branch)
    if len(matches) > 0:
        return [match.upper() for match in matches]
    else:
        return []


def _issue_is_in_message(issue_id: str, message: str) -> bool:
    """Determine if the issue ID is already in the message.

    Ignores lines in the message that start with '#'.

    Args:
        issue_id (str): the issue ID against which to check.
        message (str): the message to be checked

    Returns:
        bool: True if the issue ID is found, otherwise False.
    """
    lines = [
        line.strip() for line in message.split("\n") if not line.strip().startswith("#")
    ]
    for line in lines:
        if issue_id in line:
            return True
    return False


def _insert_issue_into_message(issue_id: str, message: str, template: str) -> str:
    """Insert the issue_id into the commit message according to the template.

    The existing message is parsed into two parts:
    - "Subject" is the first line, if that line is not a comment.
    - "Body" is the remainder of the message that is not included in "subject".

    If the first line of the message is a comment, the template is ignored and the ID
    is inserted as a new line above the existing message.

    Args:
        issue_id (str): the ID string to be inserted
        message (str): the current contents of the commit message
        template (str): a format string dictating how the output is to be arranged.
        Must contain keywords "subject", "body", and "issue_id".

    Returns:
        str: _description_
    """
    fallback_template = "[{issue_id}]\n{message}"

    for keyword in ["subject", "body", "issue_id"]:
        assert keyword in template

    content_sections: list = [line.strip() for line in message.split("\n", maxsplit=1)]
    subject: str = content_sections[0]
    body: str
    if len(content_sections) == 2:
        body = content_sections[1]
    else:
        body = ""

    if subject.startswith("#"):
        return fallback_template.format(issue_id=issue_id, message=message).strip()

    if body.startswith("#"):
        body = f"\n{body}"

    return template.format(
        subject=subject,
        issue_id=issue_id,
        body=body,
    ).strip()


def main():
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("commit_msg_filepath")
    parser.add_argument(
        "-t",
        "--template",
        default="{subject}\n\n[{issue_id}]\n{body}",
        help=(
            "Template for commit message. "
            "Must contain {subject}, {issue_id} and {body} keywords."
        ),
    )
    args = parser.parse_args()
    commit_msg_filepath = args.commit_msg_filepath
    template = args.template

    branch: str = _get_branch_name()
    issue_ids: str = _get_issue_ids_from_branch_name(branch)

    if len(issue_ids) > 0:
        issue_id: str = issue_ids[0]
        message: str

        with open(commit_msg_filepath, "r+") as f:
            message = f.read()

            if _issue_is_in_message(issue_id, message):
                return

            message = _insert_issue_into_message(issue_id, message, template)

            f.seek(0, 0)
            f.write(message)


if __name__ == "__main__":
    exit(main())
