# Copyright (c) 2023 Benjamin Mummery

import datetime
from pathlib import Path

import pytest
from freezegun import freeze_time
from pytest import CaptureFixture
from pytest_git import GitRepo
from pytest_mock import MockerFixture

from src.add_copyright_hook import add_copyright
from tests.conftest import (
    SUPPORTED_LANGUAGES,
    VALID_COPYRIGHT_STRINGS,
    SupportedLanguage,
    assert_matching,
)

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
    @pytest.mark.parametrize("language", SUPPORTED_LANGUAGES)
    @pytest.mark.parametrize("copyright_string", VALID_COPYRIGHT_STRINGS)
    def test_all_changed_files_have_copyright(
        capsys: CaptureFixture,
        copyright_string: str,
        cwd,
        language: SupportedLanguage,
        mocker: MockerFixture,
        tmp_path: Path,
    ):
        # GIVEN
        file = "hello" + language.extension
        file_content = (
            language.comment_format.format(content=copyright_string)
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
@pytest.mark.parametrize("language", SUPPORTED_LANGUAGES)
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
            cwd,
            git_repo: GitRepo,
            git_username: str,
            language: SupportedLanguage,
            mocker: MockerFixture,
        ):
            # GIVEN
            file = "hello" + language.extension
            (git_repo.workspace / file).write_text("")
            mocker.patch("sys.argv", ["stub_name", file])
            git_repo.run(f"git config user.name '{git_username}'")

            # WHEN
            with cwd(git_repo.workspace):
                assert add_copyright.main() == 1

            # THEN
            # Construct expected outputs
            copyright_string = language.comment_format.format(
                content=f"Copyright (c) 1066 {git_username}"
            )
            expected_content = f"{copyright_string}\n"
            expected_stdout = f"Fixing file `hello{language.extension}` - added line(s):\n{copyright_string}\n"  # noqa: E501

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

    class TestFileContentHandling:
        @staticmethod
        @freeze_time("1066-01-01")
        def test_adding_copyright_to_files_with_content(
            capsys: CaptureFixture,
            cwd,
            git_repo: GitRepo,
            git_username: str,
            language: SupportedLanguage,
            mocker: MockerFixture,
        ):
            # GIVEN
            file = "hello" + language.extension
            (git_repo.workspace / file).write_text(f"<file {file} content sentinel>")
            mocker.patch("sys.argv", ["stub_name", file])
            git_repo.run(f"git config user.name '{git_username}'")

            # WHEN
            with cwd(git_repo.workspace):
                assert add_copyright.main() == 1

            # THEN
            # Construct expected outputs
            copyright_string = language.comment_format.format(
                content=f"Copyright (c) 1066 {git_username}"
            )
            expected_content = (
                copyright_string + f"\n\n<file {file} content sentinel>\n"
            )
            expected_stdout = f"Fixing file `hello{language.extension}` - added line(s):\n{copyright_string}\n"  # noqa: E501

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
            cwd,
            file_content: str,
            git_repo: GitRepo,
            git_username: str,
            language: SupportedLanguage,
            mocker: MockerFixture,
        ):
            # GIVEN
            file = "hello" + language.extension
            (git_repo.workspace / file).write_text(file_content)
            mocker.patch("sys.argv", ["stub_name", file])
            git_repo.run(f"git config user.name '{git_username}'")

            # WHEN
            with cwd(git_repo.workspace):
                assert add_copyright.main() == 1

            # THEN
            # Construct expected outputs
            copyright_string = language.comment_format.format(
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
            cwd,
            git_repo: GitRepo,
            git_username: str,
            language: SupportedLanguage,
            mocker: MockerFixture,
        ):
            """
            Freezegun doesn't work on the git_repo.run subprocesses, so we use the
            current year as the year for the initial commit and set the frozen date for
            running the hook arbitrarily far into the future.
            """
            # GIVEN
            file = "hello" + language.extension
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
            copyright_string = language.comment_format.format(
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
    class TestCLIArgs:
        """
        Test the args that can be passed to the hook via the "args" section of the
        .pre-commit-config.yaml entry.
        """

        @staticmethod
        @freeze_time("1066-01-01")
        def test_custom_name_argument_overrules_git_username(
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

        @staticmethod
        @freeze_time("1066-01-01")
        def test_custom_name_argument_overrules_config_file(
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

            config_file = "pyproject.toml"
            (git_repo.workspace / config_file).write_text(
                '[tool.add_copyright]\nname="<config file username sentinel>"\n'
            )

            # WHEN
            with cwd(git_repo.workspace):
                assert add_copyright.main() == 1

            # THEN
            # Construct expected outputs
            copyright_string = "# Copyright (c) 1066 <arg name sentinel>"
            expected_content = f"{copyright_string}\n"
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

    class TestConfigFiles:
        @staticmethod
        @freeze_time("1066-01-01")
        @pytest.mark.parametrize(
            "config_file, config_file_content",
            [
                (
                    "pyproject.toml",
                    '[tool.add_copyright]\nname="<config file username sentinel>"\n',
                )
            ],
        )
        def test_custom_name_option_overrules_git_username(
            capsys: CaptureFixture,
            cwd,
            config_file: str,
            config_file_content: str,
            git_repo: GitRepo,
            mocker: MockerFixture,
        ):
            # GIVEN
            file = "hello.py"
            (git_repo.workspace / file).write_text("")
            git_repo.run("git config user.name '<git config username sentinel>'")
            mocker.patch("sys.argv", ["stub_name", file])

            (git_repo.workspace / config_file).write_text(config_file_content)

            # WHEN
            with cwd(git_repo.workspace):
                assert add_copyright.main() == 1

            # THEN
            # Construct expected outputs
            copyright_string = "# Copyright (c) 1066 <config file username sentinel>"
            expected_content = f"{copyright_string}\n"
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

        @staticmethod
        def test_raises_valueerror_for_unsupported_config_options(
            cwd,
            tmp_path: Path,
            mocker: MockerFixture,
        ):
            # GIVEN
            file = "hello.py"
            (tmp_path / file).write_text("")
            mocker.patch("sys.argv", ["stub_name", file])

            config_file = "pyproject.toml"
            (tmp_path / config_file).write_text(
                '[tool.add_copyright]\nunsupported_option="should not matter"\n'
            )

            # WHEN
            with cwd(tmp_path):
                with pytest.raises(ValueError) as e:
                    add_copyright.main()

            # THEN
            assert_matching(
                "Output error string",
                "Expected error string",
                e.exconly(),
                f"ValueError: Unsupported option in config file {tmp_path/ config_file}: 'unsupported_option'. Supported options are: ['name', 'python'].",  # noqa: E501
            )

        @staticmethod
        @pytest.mark.parametrize(
            "language, lang_ext, config_format",
            [
                (
                    "python",
                    ".py",
                    "################################################################################\n# © Copyright {year} {name}\n################################################################################",  # noqa: E501
                ),
            ],
        )
        @freeze_time("1066-01-01")
        def test_custom_formatting(
            config_format: str,
            cwd,
            git_repo: GitRepo,
            language: str,
            lang_ext: str,
            mocker: MockerFixture,
        ):
            # GIVEN
            files = [f"hello{lang.extension}" for lang in SUPPORTED_LANGUAGES]
            for file in files:
                (git_repo.workspace / file).write_text("")
            git_repo.run("git config user.name '<git config username sentinel>'")
            mocker.patch("sys.argv", ["stub_name"] + files)

            config_file = "pyproject.toml"
            (git_repo.workspace / config_file).write_text(
                f'[tool.add_copyright.{language}]\nformat="""{config_format}"""\n'
            )

            # WHEN
            with cwd(git_repo.workspace):
                assert add_copyright.main() == 1

            # THEN
            for lang in SUPPORTED_LANGUAGES:
                if lang.extension == lang_ext:
                    copyright_string = config_format.format(
                        name="<git config username sentinel>", year="1066"
                    )
                else:
                    copyright_string = lang.comment_format.format(
                        content="Copyright (c) {year} {name}".format(
                            name="<git config username sentinel>", year="1066"
                        )
                    )

                with open(git_repo.workspace / f"hello{lang.extension}", "r") as f:
                    output_content = f.read()
                assert_matching(
                    "output content",
                    "expected content",
                    output_content,
                    f"{copyright_string}\n",
                )
