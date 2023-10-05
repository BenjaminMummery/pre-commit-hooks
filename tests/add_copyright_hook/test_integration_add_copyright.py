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
class TestDefaultBehaviour:
    @staticmethod
    def test_adding_copyright_to_empty_files(
        capsys: CaptureFixture,
        comment_format: str,
        cwd,
        git_repo: GitRepo,
        extension: str,
        mocker: MockerFixture,
        tmp_path: Path,
    ):
        # GIVEN
        file = "hello" + extension
        (tmp_path / file).write_text("")
        mocker.patch("sys.argv", ["stub_name", file])
        git_repo.run("git config user.name '<git config username sentinel>'")

        # WHEN
        with cwd(tmp_path):
            assert add_copyright.main() == 1

        # THEN
        expected_content = (
            comment_format.format(
                content=f"Copyright (c) {THIS_YEAR} <git config username sentinel>"
            )
            + "\n"
        )
        with open(tmp_path / file, "r") as f:
            output_content = f.read()

        assert output_content == expected_content
        captured = capsys.readouterr()
        assert captured.out == ""
        assert captured.err == ""

    @staticmethod
    def test_adding_copyright_to_files_with_content(
        capsys: CaptureFixture,
        comment_format: str,
        cwd,
        git_repo: GitRepo,
        extension: str,
        mocker: MockerFixture,
        tmp_path: Path,
    ):
        # GIVEN
        file = "hello" + extension
        (tmp_path / file).write_text(f"<file {file} content sentinel>")
        mocker.patch("sys.argv", ["stub_name", file])
        git_repo.run("git config user.name '<git config username sentinel>'")

        # WHEN
        with cwd(tmp_path):
            assert add_copyright.main() == 1

        # THEN
        with open(tmp_path / file, "r") as f:
            output_content = f.read()
        captured = capsys.readouterr()
        expected_content = (
            comment_format.format(
                content=f"Copyright (c) {THIS_YEAR} <git config username sentinel>"
            )
            + f"\n\n<file {file} content sentinel>\n"
        )

        print(output_content)
        print("=" * 80)
        print(expected_content)
        assert output_content == expected_content
        assert captured.out == ""
        assert captured.err == ""
