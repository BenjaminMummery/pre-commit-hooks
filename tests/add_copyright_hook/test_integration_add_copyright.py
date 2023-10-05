# Copyright (c) 2023 Benjamin Mummery

import datetime
from pathlib import Path

import pytest
from pytest import CaptureFixture
from pytest_git import GitRepo
from pytest_mock import MockerFixture

from src.add_copyright_hook import add_copyright

THIS_YEAR = datetime.date.today().year


class TestNoChanges:
    @staticmethod
    def test_no_files_changed(
        capsys: CaptureFixture,
        mocker: MockerFixture,
    ):
        mocker.patch("sys.argv", ["stub_name"])

        assert add_copyright.main() == 0
        captured = capsys.readouterr()
        assert captured.out == ""
        assert captured.err == ""

    @staticmethod
    @pytest.mark.parametrize(
        "extension, comment_format",
        [
            (".py", "# {content}"),
            (".md", "<!--- {content} -->"),
            (".cpp", "// {content}"),
            (".cs", "/* {content} */"),
            (".pl", "# {content}"),
        ],
    )
    @pytest.mark.parametrize(
        "copyright_string",
        [
            "Copyright 1111 NAME",
            "Copyright (c) 1111 NAME",
            "(c) 1111 NAME",
        ],
    )
    def test_all_changed_files_have_copyright(
        capsys: CaptureFixture,
        comment_format: str,
        copyright_string: str,
        cwd,
        extension: str,
        mocker: MockerFixture,
        tmp_path: Path,
    ):
        # GIVEN
        file = "hello" + extension
        file_content = (
            comment_format.format(content=copyright_string)
            + "\n\n<file content sentinel>"
        )
        (tmp_path / file).write_text(file_content)
        mocker.patch("sys.argv", ["stub_name", file])

        # WHEN
        with cwd(tmp_path):
            assert add_copyright.main() == 0

        # THEN
        with open(tmp_path / file, "r") as f:
            output_content = f.read()
        assert output_content == file_content
        captured = capsys.readouterr()
        assert captured.out == ""
        assert captured.err == ""


# Check for every language we support
@pytest.mark.parametrize(
    "extension, comment_format",
    [
        (".py", "# {content}"),
        (".md", "<!--- {content} -->"),
        (".cpp", "// {content}"),
        (".cs", "/* {content} */"),
        (".pl", "# {content}"),
    ],
)
# Check multiple usernames to confirm they get read in correctly.
@pytest.mark.parametrize(
    "git_username", ["<git config username sentinel>", "Taylor Swift"]
)
class TestDefaultBehaviour:
    @staticmethod
    def test_adding_copyright_to_empty_files(
        capsys: CaptureFixture,
        comment_format: str,
        cwd,
        git_repo: GitRepo,
        git_username: str,
        extension: str,
        mocker: MockerFixture,
    ):
        # GIVEN
        file = "hello" + extension
        (git_repo.workspace / file).write_text("")
        mocker.patch("sys.argv", ["stub_name", file])
        git_repo.run(f"git config user.name '{git_username}'")

        # WHEN
        with cwd(git_repo.workspace):
            assert add_copyright.main() == 1

        # THEN
        copyright_string = comment_format.format(
            content=f"Copyright (c) {THIS_YEAR} {git_username}"
        )
        expected_content = f"{copyright_string}\n"
        expected_stdout = (
            f"Fixing file `hello{extension}` - added line(s):\n{copyright_string}\n"
        )
        with open(git_repo.workspace / file, "r") as f:
            output_content = f.read()

        assert output_content == expected_content
        captured = capsys.readouterr()
        assert captured.out == expected_stdout
        assert captured.err == ""

    @staticmethod
    def test_adding_copyright_to_files_with_content(
        capsys: CaptureFixture,
        comment_format: str,
        cwd,
        git_repo: GitRepo,
        git_username: str,
        extension: str,
        mocker: MockerFixture,
    ):
        # GIVEN
        file = "hello" + extension
        (git_repo.workspace / file).write_text(f"<file {file} content sentinel>")
        mocker.patch("sys.argv", ["stub_name", file])
        git_repo.run(f"git config user.name '{git_username}'")

        # WHEN
        with cwd(git_repo.workspace):
            assert add_copyright.main() == 1

        # THEN
        copyright_string = comment_format.format(
            content=f"Copyright (c) {THIS_YEAR} {git_username}"
        )
        expected_content = copyright_string + f"\n\n<file {file} content sentinel>\n"
        expected_stdout = (
            f"Fixing file `hello{extension}` - added line(s):\n{copyright_string}\n"
        )
        with open(git_repo.workspace / file, "r") as f:
            output_content = f.read()
        captured = capsys.readouterr()

        assert output_content == expected_content
        assert captured.out == expected_stdout
        assert captured.err == ""
