# Copyright (c) 2023 Benjamin Mummery

import datetime
from pathlib import Path
from typing import List, Union

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
SUPPORTED_TOP_LEVEL_CONFIG_OPTIONS = [
    "name",
    "format",
    "python",
    "markdown",
    "cpp",
    "c-sharp",
    "perl",
]
SUPPORTED_PER_LANGUAGE_CONFIG_OPTIONS = ["format"]


def add_changed_files(
    filenames: Union[str, List[str]],
    contents: Union[str, List[str]],
    git_repo: GitRepo,
    mocker: MockerFixture,
):
    if not isinstance(filenames, list):
        filenames = [filenames]
    if not isinstance(contents, list):
        contents = [contents for _ in filenames]
    for filename, content in zip(filenames, contents):
        (git_repo.workspace / filename).write_text(content)
    return mocker.patch("sys.argv", ["stub_name"] + filenames)


def write_config_file(path: Path, content: str) -> Path:
    config_file = path / "pyproject.toml"
    (config_file).write_text(content)
    return config_file


@pytest.fixture()
def git_repo(git_repo: GitRepo) -> GitRepo:
    git_repo.run("git config user.name '<git config username sentinel>'")
    return git_repo


@pytest.mark.usefixtures("git_repo")
class TestNoChanges:
    @staticmethod
    def test_no_files_changed(
        capsys: CaptureFixture,
        mocker: MockerFixture,
    ):
        # GIVEN
        mocker.patch("sys.argv", ["stub_name"])

        # WHEN
        assert add_copyright.main() == 0

        # THEN
        captured = capsys.readouterr()
        assert_matching("captured stdout", "expected stdout", captured.out, "")
        assert_matching("captured stderr", "expected stderr", captured.err, "")

    @staticmethod
    @pytest.mark.parametrize("language", SUPPORTED_LANGUAGES)
    @pytest.mark.parametrize("copyright_string", VALID_COPYRIGHT_STRINGS)
    def test_all_changed_files_have_copyright(
        # capsys: CaptureFixture,
        copyright_string: str,
        cwd,
        git_repo: GitRepo,
        language: SupportedLanguage,
        mocker: MockerFixture,
    ):
        # GIVEN
        add_changed_files(
            file := "hello" + language.extension,
            file_content := (
                language.comment_format.format(content=copyright_string)
                + "\n\n<file content sentinel>"
            ),
            git_repo,
            mocker,
        )

        # WHEN
        with cwd(git_repo.workspace):
            assert add_copyright.main() == 0

        # THEN
        # Gather actual outputs
        with open(git_repo.workspace / file, "r") as f:
            output_content = f.read()
        # captured = capsys.readouterr()

        # Compare
        assert_matching(
            "output content", "expected content", output_content, file_content
        )
        # assert_matching("captured stdout", "expected stdout", captured.out, "")
        # assert_matching("captured stderr", "expected stderr", captured.err, "")


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
            add_changed_files(
                file := "hello" + language.extension, "", git_repo, mocker
            )
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
            add_changed_files(
                file := "hello" + language.extension,
                f"<file {file} content sentinel>",
                git_repo,
                mocker,
            )
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
            add_changed_files(
                file := "hello" + language.extension, file_content, git_repo, mocker
            )
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
            """Freezegun doesn't work on the git_repo.run subprocesses, so we use the
            current year as the year for the initial commit and set the frozen date for
            running the hook arbitrarily far into the future.
            """
            # GIVEN
            add_changed_files(
                file := "hello" + language.extension,
                f"<file {file} content sentinel>",
                git_repo,
                mocker,
            )
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
        """Test the args that can be passed to the hook via the "args" section of the
        .pre-commit-config.yaml entry.
        """

        class TestName:
            @staticmethod
            @freeze_time("1066-01-01")
            def test_custom_name_argument_overrules_git_username(
                capsys: CaptureFixture,
                cwd,
                git_repo: GitRepo,
                mocker: MockerFixture,
            ):
                # GIVEN
                add_changed_files(file := "hello.py", "", git_repo, mocker)
                mocker.patch(
                    "sys.argv", ["stub_name", "-n", "<arg name sentinel>", file]
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
                    "output content",
                    "expected content",
                    output_content,
                    expected_content,
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
                add_changed_files(file := "hello.py", "", git_repo, mocker)
                mocker.patch(
                    "sys.argv", ["stub_name", "-n", "<arg name sentinel>", file]
                )
                write_config_file(
                    git_repo.workspace,
                    '[tool.add_copyright]\nname="<config file username sentinel>"\n',
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
                    "output content",
                    "expected content",
                    output_content,
                    expected_content,
                )
                assert_matching(
                    "captured stdout", "expected stdout", captured.out, expected_stdout
                )
                assert_matching("captured stderr", "expected stderr", captured.err, "")

        class TestFormat:
            @staticmethod
            @freeze_time("1066-01-01")
            def test_custom_format_argument_overrules_default(
                capsys: CaptureFixture,
                cwd,
                git_repo: GitRepo,
                mocker: MockerFixture,
            ):
                # GIVEN
                add_changed_files(file := "hello.py", "", git_repo, mocker)
                mocker.patch("sys.argv", ["stub_name", "-f", "(C) {name} {year}", file])
                write_config_file(
                    git_repo.workspace,
                    '[tool.add_copyright]\nformat="(C) not this one {name} {year}"\n',
                )

                # WHEN
                with cwd(git_repo.workspace):
                    assert add_copyright.main() == 1

                # THEN
                # Construct expected outputs
                copyright_string = "# (C) <git config username sentinel> 1066"
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
                    "output content",
                    "expected content",
                    output_content,
                    expected_content,
                )
                assert_matching(
                    "captured stdout", "expected stdout", captured.out, expected_stdout
                )
                assert_matching("captured stderr", "expected stderr", captured.err, "")

            @staticmethod
            @freeze_time("1066-01-01")
            def test_custom_format_argument_overrules_config_file(
                capsys: CaptureFixture,
                cwd,
                git_repo: GitRepo,
                mocker: MockerFixture,
            ):
                # GIVEN
                add_changed_files(file := "hello.py", "", git_repo, mocker)
                mocker.patch("sys.argv", ["stub_name", "-f", "(C) {name} {year}", file])
                write_config_file(
                    git_repo.workspace,
                    '[tool.add_copyright]\nformat="(C) not this one {name} {year}"\n',
                )

                # WHEN
                with cwd(git_repo.workspace):
                    assert add_copyright.main() == 1

                # THEN
                # Construct expected outputs
                copyright_string = "# (C) <git config username sentinel> 1066"
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
                    "output content",
                    "expected content",
                    output_content,
                    expected_content,
                )
                assert_matching(
                    "captured stdout", "expected stdout", captured.out, expected_stdout
                )
                assert_matching("captured stderr", "expected stderr", captured.err, "")

    class TestConfigFiles:
        class TestGlobalConfigs:
            @staticmethod
            @freeze_time("1066-01-01")
            @pytest.mark.parametrize(
                "config_file_content",
                [
                    '[tool.add_copyright]\nname="<config file username sentinel>"\n',
                ],
            )
            def test_custom_name_option_overrules_git_username(
                capsys: CaptureFixture,
                cwd,
                config_file_content: str,
                git_repo: GitRepo,
                mocker: MockerFixture,
            ):
                # GIVEN
                add_changed_files(file := "hello.py", "", git_repo, mocker)
                write_config_file(git_repo.workspace, config_file_content)

                # WHEN
                with cwd(git_repo.workspace):
                    assert add_copyright.main() == 1

                # THEN
                # Construct expected outputs
                copyright_string = (
                    "# Copyright (c) 1066 <config file username sentinel>"
                )
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
                    "output content",
                    "expected content",
                    output_content,
                    expected_content,
                )
                assert_matching(
                    "captured stdout", "expected stdout", captured.out, expected_stdout
                )
                assert_matching("captured stderr", "expected stderr", captured.err, "")

            @staticmethod
            def test_custom_format_option_overrules_default_format():
                pass

        @pytest.mark.parametrize("language", SUPPORTED_LANGUAGES)
        class TestPerLanguageConfigs:
            @staticmethod
            @freeze_time("1066-01-01")
            def test_custom_formatting_commented_overrules_default_format(
                cwd,
                git_repo: GitRepo,
                language: SupportedLanguage,
                mocker: MockerFixture,
            ):
                # GIVEN
                print(
                    add_changed_files(
                        [f"hello{lang.extension}" for lang in SUPPORTED_LANGUAGES],
                        "",
                        git_repo,
                        mocker,
                    )
                )
                write_config_file(
                    git_repo.workspace,
                    (
                        f"[tool.add_copyright.{language.toml_key}]\n"
                        f'format="""{language.custom_copyright_format_commented}"""\n'
                    ),
                )

                # WHEN
                with cwd(git_repo.workspace):
                    assert add_copyright.main() == 1

                # THEN
                for lang in SUPPORTED_LANGUAGES:
                    if lang.extension == language.extension:
                        # If we're looking at the language we've set up a custom format
                        # for, then we should see a copyright with that formatting.
                        copyright_string = (
                            language.custom_copyright_format_commented.format(
                                name="<git config username sentinel>", year="1066"
                            )
                        )
                    else:
                        # Otherwise we expect the default copyright format.
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

            @staticmethod
            @freeze_time("1066-01-01")
            def test_custom_formatting_uncommented_overrules_default_format(
                cwd,
                git_repo: GitRepo,
                language: SupportedLanguage,
                mocker: MockerFixture,
            ):
                # GIVEN
                add_changed_files(
                    [f"hello{lang.extension}" for lang in SUPPORTED_LANGUAGES],
                    "",
                    git_repo,
                    mocker,
                )
                write_config_file(
                    git_repo.workspace,
                    (
                        f"[tool.add_copyright.{language.toml_key}]\n"
                        f'format="""{language.custom_copyright_format_uncommented}"""\n'
                    ),
                )

                # WHEN
                with cwd(git_repo.workspace):
                    assert add_copyright.main() == 1

                # THEN
                for lang in SUPPORTED_LANGUAGES:
                    if lang.extension == language.extension:
                        # If we're looking at the language we've set up a custom format
                        # for, then we should see a copyright with that formatting.
                        copyright_string = language.comment_format.format(
                            content=language.custom_copyright_format_uncommented.format(
                                name="<git config username sentinel>", year="1066"
                            )
                        )
                    else:
                        # Otherwise we expect the default copyright format.
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


class TestFailureStates:
    @staticmethod
    @pytest.mark.parametrize(
        "config_file_content",
        [
            '[tool.add_copyright]\nunsupported_option="should not matter"\n',
            '[tool.add_copyright.unsupported_option]\nname="foo"\n',
        ],
    )
    def test_raises_KeyError_for_unsupported_config_options(
        cwd,
        git_repo: GitRepo,
        config_file_content: str,
        mocker: MockerFixture,
    ):
        # GIVEN
        add_changed_files("hello.py", "", git_repo, mocker)
        config_file = write_config_file(git_repo.workspace, config_file_content)

        # WHEN
        with cwd(git_repo.workspace):
            with pytest.raises(KeyError) as e:
                add_copyright.main()

        # THEN
        assert_matching(
            "Output error string",
            "Expected error string",
            e.exconly(),
            f"KeyError: \"Unsupported option in config file {Path('/private')}{git_repo.workspace/ config_file}: 'unsupported_option'. Supported options are: {SUPPORTED_TOP_LEVEL_CONFIG_OPTIONS}.\"",  # noqa: E501
        )

    @staticmethod
    @pytest.mark.parametrize(
        "config_file_content",
        [
            '[tool.add_copyright.{language}]\nunsupported_option="should not matter"\n',
        ],
    )
    @pytest.mark.parametrize("language", SUPPORTED_LANGUAGES)
    def test_raises_KeyError_for_unsupported_language_config_options(
        cwd,
        config_file_content: str,
        git_repo: GitRepo,
        language: SupportedLanguage,
        mocker: MockerFixture,
    ):
        # GIVEN
        add_changed_files("hello.py", "", git_repo, mocker)
        config_file = write_config_file(
            git_repo.workspace, config_file_content.format(language=language.toml_key)
        )

        # WHEN
        with cwd(git_repo.workspace):
            with pytest.raises(KeyError) as e:
                add_copyright.main()

        # THEN
        assert_matching(
            "Output error string",
            "Expected error string",
            e.exconly(),
            f"KeyError: \"Unsupported option in config file {Path('/private')}{git_repo.workspace/ config_file}: '{language.toml_key}.unsupported_option'. Supported options for '{language.toml_key}' are: {SUPPORTED_PER_LANGUAGE_CONFIG_OPTIONS}.\"",  # noqa: E501
        )

    @staticmethod
    @pytest.mark.parametrize(
        "input_format, missing_keys",
        [
            ("copyright 1996 {name}", "year"),
            ("copyright {year} Harold Hadrada", "name"),
        ],
    )
    @pytest.mark.parametrize("language", SUPPORTED_LANGUAGES)
    def test_raises_KeyError_for_missing_custom_format_keys(
        cwd,
        git_repo: GitRepo,
        input_format: str,
        language: SupportedLanguage,
        missing_keys: str,
        mocker: MockerFixture,
    ):
        # GIVEN
        add_changed_files("hello" + language.extension, "", git_repo, mocker)

        write_config_file(
            git_repo.workspace,
            f'[tool.add_copyright.{language.toml_key}]\nformat="{input_format}"\n',
        )

        # WHEN
        with cwd(git_repo.workspace):
            with pytest.raises(KeyError) as e:
                add_copyright.main()

        # THEN
        assert_matching(
            "Output error string",
            "Expected error string",
            e.exconly(),
            f"KeyError: \"The format string '{input_format}' is missing the following required keys: ['{missing_keys}']\"",  # noqa: E501
        )
