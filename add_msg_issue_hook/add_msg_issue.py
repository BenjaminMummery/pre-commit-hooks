#!/usr/bin/env python3

import argparse
import re
import subprocess

DEFAULT_TEMPLATE: str = "{subject}\n\n[{issue_id}]\n{body}"
FALLBACK_TEMPLATE: str = "{message}\n[{issue_id}]"


def _get_branch_name() -> str:
    """Get the name of the current git branch.

    Returns:
        str: The branch name. this string will be empty if we're not in a git repo.
    """
    branch: str = ""
    try:
        branch = subprocess.check_output(
            ["git", "symbolic-ref", "--short", "HEAD"], universal_newlines=True
        ).strip()
    except Exception as e:
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
        str: the modified message.
    """
    content_sections: list = [line.strip() for line in message.split("\n", maxsplit=1)]
    subject: str = content_sections[0]
    body: str = ""
    if len(content_sections) > 1:
        body = " ".join(content_sections[1:])

    if subject.startswith("#"):
        return FALLBACK_TEMPLATE.format(issue_id=issue_id, message=message).strip()

    if body.startswith("#"):
        # Depending on the template, a body starting with a comment could be appended
        # to a non-comment line, meaning that git will not ignore it in the message. To
        # avoid this, we add a newline so that the # character always comes at the start
        # of the line.
        body = f"\n{body}"

    return template.format(
        subject=subject,
        issue_id=issue_id,
        body=body,
    ).strip()


def _parse_args() -> argparse.Namespace:
    """Parse the CLI arguments.

    Returns:
        argparse.Namespace with the following attributes:
        - commit_msg_filepath (str): path to the location of the commit message
        - template (str): the template into which to render the commit message.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("commit_msg_filepath")
    parser.add_argument(
        "-t",
        "--template",
        default=DEFAULT_TEMPLATE,
        help=(
            "Template for commit message. "
            "Must contain {subject}, {issue_id} and {body} keywords."
        ),
    )
    args = parser.parse_args()

    print("PARSED TEMPLATE:", args.template)

    fallback_message = (
        rf"The default template '{DEFAULT_TEMPLATE}' will be used instead. "
        "For more information, see "
        "https://github.com/BenjaminMummery/pre-commit-hooks"
    )
    for keyword in [r"{subject}", r"{body}", r"{issue_id}"]:
        if keyword not in args.template:
            print(
                rf"Template argument '{args.template}' did not contain the required "
                f"keyword {{keyword}} and cannot be used. " + fallback_message
            )
            args.template = DEFAULT_TEMPLATE
            break
    try:
        args.template.format(subject="s", body="b", issue_id="i")
    except KeyError as e:
        print(
            rf"Template argument '{args.template}' contained unrecognised keywords: "
            + str(e)
            + fallback_message
        )
        args.template = DEFAULT_TEMPLATE

    return args


def main():
    args = _parse_args()

    issue_ids: str = _get_issue_ids_from_branch_name(_get_branch_name())
    if len(issue_ids) < 1:
        return  # If no IDs are found, then there's nothing to do

    with open(args.commit_msg_filepath, "r+") as f:
        message: str = f.read()

        if _issue_is_in_message(issue_ids[0], message):
            return  # If the ID is already in the message, then there's nothing to do

        f.seek(0, 0)
        f.write(_insert_issue_into_message(issue_ids[0], message, args.template))


if __name__ == "__main__":
    exit(main())
