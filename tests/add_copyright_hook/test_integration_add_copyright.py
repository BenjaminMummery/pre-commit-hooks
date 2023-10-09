# Copyright (c) 2023 Benjamin Mummery

import datetime
from pathlib import Path

import pytest
from freezegun import freeze_time
from pytest import CaptureFixture
from pytest_git import GitRepo
from pytest_mock import MockerFixture

from src.add_copyright_hook import add_copyright
from tests.conftest import SUPPORTED_FILES, VALID_COPYRIGHT_STRINGS, assert_matching

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
        assert_matching("captured stdout", "expected stdout", captured.out, "")
        assert_matching("captured stderr", "expected stderr", captured.err, "")

    @staticmethod
    @pytest.mark.parametrize("extension, comment_format", SUPPORTED_FILES)
    @pytest.mark.parametrize(
        "copyright_string",
        VALID_COPYRIGHT_STRINGS,
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
        # Gather actual outputs
        with open(tmp_path / file, "r") as f:
            output_content = f.read()
        captured = capsys.readouterr()

        # Compare
        assert_matching(
            "output content", "expected content", output_content, file_content
        )
        assert_matching("captured stdout", "expected stdout", captured.out, "")
        assert_matching("captured stderr", "expected stderr", captured.err, "")


# Check for every language we support
@pytest.mark.parametrize("extension, comment_format", SUPPORTED_FILES)
# Check multiple usernames to confirm they get read in correctly.
@pytest.mark.parametrize(
    "git_username", ["<git config username sentinel>", "Taylor Swift"]
)
class TestDefaultBehaviour:
    class TestEmptyFiles:
        @staticmethod
        @freeze_time("1066-01-01")
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
            # Construct expected outputs
            copyright_string = comment_format.format(
                content=f"Copyright (c) 1066 {git_username}"
            )
            expected_content = f"{copyright_string}\n"
            expected_stdout = (
                f"Fixing file `hello{extension}` - added line(s):\n{copyright_string}\n"
            )

            # Gather actual outputs
            with open(git_repo.workspace / file, "r") as f:
                output_content = f.read()
            captured = capsys.readouterr()

            # Compare
            assert_matching(
                "output content", "expected content", output_content, expected_content
            )
            assert_matching(
                "captured stdout", "expected stdout", captured.out, expected_stdout
            )
            assert_matching("captured stderr", "expected stderr", captured.err, "")

    class TestHandlesFileContent:
        @staticmethod
        @freeze_time("1066-01-01")
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
            # Construct expected outputs
            copyright_string = comment_format.format(
                content=f"Copyright (c) 1066 {git_username}"
            )
            expected_content = (
                copyright_string + f"\n\n<file {file} content sentinel>\n"
            )
            expected_stdout = (
                f"Fixing file `hello{extension}` - added line(s):\n{copyright_string}\n"
            )

            # Gather actual outputs
            with open(git_repo.workspace / file, "r") as f:
                output_content = f.read()
            captured = capsys.readouterr()

            # Compare
            assert_matching(
                "output content", "expected content", output_content, expected_content
            )
            assert_matching(
                "captured stdout", "expected stdout", captured.out, expected_stdout
            )
            assert_matching("captured stderr", "expected stderr", captured.err, "")

        @staticmethod
        @freeze_time("1066-01-01")
        @pytest.mark.parametrize(
            "file_content",
            [
                "#!/usr/bin/env python3\n<file content sentinel>",
                "#!/usr/bin/env python3\n\n<file content sentinel>",
            ],
        )
        def test_handles_shebang(
            capsys: CaptureFixture,
            comment_format: str,
            cwd,
            file_content: str,
            git_repo: GitRepo,
            git_username: str,
            extension: str,
            mocker: MockerFixture,
        ):
            # GIVEN
            file = "hello" + extension
            (git_repo.workspace / file).write_text(file_content)
            mocker.patch("sys.argv", ["stub_name", file])
            git_repo.run(f"git config user.name '{git_username}'")

            # WHEN
            with cwd(git_repo.workspace):
                assert add_copyright.main() == 1

            # THEN
            # Construct expected outputs
            copyright_string = comment_format.format(
                content=f"Copyright (c) 1066 {git_username}"
            )
            expected_content = (
                "#!/usr/bin/env python3\n"
                "\n"
                f"{copyright_string}\n"
                "\n"
                f"<file content sentinel>\n"
            )
            expected_stdout = (
                f"Fixing file `{file}` - added line(s):\n{copyright_string}\n"
            )

            # Gather actual outputs
            with open(git_repo.workspace / file, "r") as f:
                output_content = f.read()
            captured = capsys.readouterr()

            # Compare
            assert_matching(
                "output content", "expected content", output_content, expected_content
            )
            assert_matching(
                "captured stdout", "expected stdout", captured.out, expected_stdout
            )
            assert_matching("captured stderr", "expected stderr", captured.err, "")

    class TestDateHandling:
        @staticmethod
        @freeze_time("9999-01-01")
        def test_infers_start_date_from_git_history(
            capsys: CaptureFixture,
            comment_format: str,
            cwd,
            git_repo: GitRepo,
            git_username: str,
            extension: str,
            mocker: MockerFixture,
        ):
            """
            Freezegun doesn't work on the git_repo.run subprocesses, so we use the
            current year as the year for the initial commit and set the frozen date for
            running the hook arbitrarily far into the future.
            """
            # GIVEN
            file = "hello" + extension
            (git_repo.workspace / file).write_text(f"<file {file} content sentinel>")
            mocker.patch("sys.argv", ["stub_name", file])
            git_repo.run(f"git config user.name '{git_username}'")
            git_repo.run(f"git add {file}", check_rc=True)
            git_repo.run("git commit -m 'test commit' --no-verify", check_rc=True)

            # WHEN
            with cwd(git_repo.workspace):
                assert add_copyright.main() == 1

            # THEN
            # Construct expected outputs
            copyright_string = comment_format.format(
                content=f"Copyright (c) {THIS_YEAR} - 9999 {git_username}"
            )
            expected_content = f"{copyright_string}\n\n<file {file} content sentinel>\n"
            expected_stdout = (
                f"Fixing file `{file}` - added line(s):\n{copyright_string}\n"
            )

            # Gather actual outputs
            with open(git_repo.workspace / file, "r") as f:
                output_content = f.read()
            captured = capsys.readouterr()

            # Compare
            assert_matching(
                "output content", "expected content", output_content, expected_content
            )
            assert_matching(
                "captured stdout", "expected stdout", captured.out, expected_stdout
            )
            assert_matching("captured stderr", "expected stderr", captured.err, "")


class TestCustomBehaviour:
    @staticmethod
    @freeze_time("1066-01-01")
    def test_custom_argument_overrules_git_username(
        capsys: CaptureFixture,
        cwd,
        git_repo: GitRepo,
        mocker: MockerFixture,
    ):
        # GIVEN
        file = "hello.py"
        (git_repo.workspace / file).write_text("")
        mocker.patch("sys.argv", ["stub_name", "-n", "<arg name sentinel>", file])
        git_repo.run("git config user.name '<git config username sentinel>'")

        # WHEN
        with cwd(git_repo.workspace):
            assert add_copyright.main() == 1

        # THEN
        # Construct expected outputs
        copyright_string = "# Copyright (c) 1066 <arg name sentinel>"
        expected_content = f"{copyright_string}\n"
        expected_stdout = f"Fixing file `{file}` - added line(s):\n{copyright_string}\n"

        # Gather actual outputs
        with open(git_repo.workspace / file, "r") as f:
            output_content = f.read()
        captured = capsys.readouterr()

        # Compare
        assert_matching(
            "output content", "expected content", output_content, expected_content
        )
        assert_matching(
            "captured stdout", "expected stdout", captured.out, expected_stdout
        )
        assert_matching("captured stderr", "expected stderr", captured.err, "")
