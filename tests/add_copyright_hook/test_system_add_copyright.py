# Copyright (c) 2022-2024 Benjamin Mummery

import datetime
import os
import subprocess
from pathlib import Path

import pytest
from pytest_git import GitRepo

from conftest import (
    CopyrightGlobals,
    SupportedLanguage,
    add_changed_files,
    assert_matching,
    write_config_file,
)

COMMAND = ["pre-commit", "try-repo", f"{os.getcwd()}", "add-copyright"]
THIS_YEAR = datetime.date.today().year


class TestNoChanges:
    @staticmethod
    def test_no_files_changed(git_repo: GitRepo, cwd):
        """No files have been changed, nothing to check."""
        with cwd(git_repo.workspace):
            process: subprocess.CompletedProcess = subprocess.run(
                COMMAND, capture_output=True, text=True
            )

        assert process.returncode == 0, process.stdout + process.stderr
        assert "Add copyright string to source files" in process.stdout
        assert "Passed" in process.stdout

    @staticmethod
    def test_no_supported_files_changed(git_repo: GitRepo, cwd):
        """Files have been changed, but none of them are in languages we support."""
        # GIVEN
        files = ["hello.txt", ".gitignore", "test.yaml"]
        for file in files:
            f = git_repo.workspace / file
            f.write_text(f"<file {file} content sentinel>")
            git_repo.run(f"git add {file}")

        # WHEN
        with cwd(git_repo.workspace):
            process: subprocess.CompletedProcess = subprocess.run(
                COMMAND, capture_output=True, text=True
            )

        # THEN
        assert process.returncode == 0, process.stdout + process.stderr
        for file in files:
            with open(git_repo.workspace / file, "r") as f:
                content = f.read()
            assert content == f"<file {file} content sentinel>"
        assert "Add copyright string to source files" in process.stdout
        assert "Passed" in process.stdout

    @staticmethod
    @pytest.mark.parametrize("language", CopyrightGlobals.SUPPORTED_LANGUAGES)
    @pytest.mark.parametrize(
        "copyright_string",
        [
            s.format(end_year=THIS_YEAR)
            for s in CopyrightGlobals.VALID_COPYRIGHT_STRINGS
        ],
    )
    def test_all_changed_files_have_copyright(
        git_repo: GitRepo,
        cwd,
        language: SupportedLanguage,
        copyright_string: str,
    ):
        """Files have been changed, but all have valid copyright strings."""
        # GIVEN
        file = "hello" + language.extension
        file_content = (
            language.comment_format.format(content=copyright_string)
            + "\n\n<file content sentinel>"
        )
        (git_repo.workspace / file).write_text(file_content)
        git_repo.run(f"git add {file}")

        # WHEN
        with cwd(git_repo.workspace):
            process: subprocess.CompletedProcess = subprocess.run(
                COMMAND, capture_output=True, text=True
            )

        # THEN
        assert process.returncode == 0, process.stdout + process.stderr
        with open(git_repo.workspace / file, "r") as f:
            output_content = f.read()
        assert_matching(
            "output content", "expected content", output_content, file_content
        )
        assert "Add copyright string to source files" in process.stdout
        assert "Passed" in process.stdout


# Check multiple usernames to confirm they get read in correctly.
@pytest.mark.parametrize(
    "git_username", ["<git config username sentinel>", "Taylor Swift"]
)
class TestDefaultBehaviour:
    class TestEmptyFiles:
        @staticmethod
        def test_adding_copyright_to_empty_files(
            cwd,
            git_repo: GitRepo,
            git_username: str,
        ):
            """The simplest case - the changed files are all empty, so we're not worried
            about overwriting or corrupting content.
            """
            # GIVEN
            git_repo.run(f"git config user.name '{git_username}'")
            add_changed_files(
                [
                    f"hello{lang.extension}"
                    for lang in CopyrightGlobals.SUPPORTED_LANGUAGES
                ],
                "",
                git_repo,
            )

            # WHEN
            with cwd(git_repo.workspace):
                process: subprocess.CompletedProcess = subprocess.run(
                    COMMAND, capture_output=True, text=True
                )

            # THEN
            assert process.returncode == 1, process.stdout + process.stderr

            for language in CopyrightGlobals.SUPPORTED_LANGUAGES:
                file = "hello" + language.extension
                copyright_string = language.comment_format.format(
                    content=f"Copyright (c) {THIS_YEAR} {git_username}"
                )
                expected_content = f"{copyright_string}\n"
                expected_stdout = (
                    f"Fixing file `{file}` - added line(s):\n{copyright_string}\n"
                )
                with open(git_repo.workspace / file, "r") as f:
                    output_content = f.read()

                assert_matching(
                    "output content",
                    "expected content",
                    output_content,
                    expected_content,
                )
                assert expected_stdout in process.stdout

    class TestFileContentHandling:
        @staticmethod
        def test_adding_copyright_to_files_with_content(
            cwd,
            git_repo: GitRepo,
            git_username: str,
        ):
            # GIVEN
            git_repo.run(f"git config user.name '{git_username}'")
            add_changed_files(
                [
                    f"hello{lang.extension}"
                    for lang in CopyrightGlobals.SUPPORTED_LANGUAGES
                ],
                [
                    f"<file hello{lang.extension} content sentinel>"
                    for lang in CopyrightGlobals.SUPPORTED_LANGUAGES
                ],
                git_repo,
            )

            # WHEN
            with cwd(git_repo.workspace):
                process: subprocess.CompletedProcess = subprocess.run(
                    COMMAND, capture_output=True, text=True
                )

            # THEN
            assert process.returncode == 1, process.stdout + process.stderr
            for language in CopyrightGlobals.SUPPORTED_LANGUAGES:
                file = "hello" + language.extension
                copyright_string = language.comment_format.format(
                    content=f"Copyright (c) {THIS_YEAR} {git_username}"
                )
                expected_content = (
                    copyright_string + f"\n\n<file {file} content sentinel>\n"
                )
                expected_stdout = (
                    f"Fixing file `{file}` - added line(s):\n{copyright_string}\n"
                )
                with open(git_repo.workspace / file, "r") as f:
                    output_content = f.read()

                assert_matching(
                    "output content",
                    "expected content",
                    output_content,
                    expected_content,
                )
                assert expected_stdout in process.stdout

        @staticmethod
        def test_handles_shebang(
            cwd,
            git_repo: GitRepo,
            git_username: str,
        ):
            # GIVEN
            git_repo.run(f"git config user.name '{git_username}'")
            add_changed_files(
                [
                    f"hello{lang.extension}"
                    for lang in CopyrightGlobals.SUPPORTED_LANGUAGES
                ],
                [
                    f"#!/usr/bin/env python3\n<file hello{lang.extension} content sentinel>"  # noqa: E501
                    for lang in CopyrightGlobals.SUPPORTED_LANGUAGES
                ],
                git_repo,
            )

            # WHEN
            with cwd(git_repo.workspace):
                process: subprocess.CompletedProcess = subprocess.run(
                    COMMAND, capture_output=True, text=True
                )

            # THEN
            assert process.returncode == 1, process.stdout + process.stderr
            for language in CopyrightGlobals.SUPPORTED_LANGUAGES:
                file = "hello" + language.extension
                copyright_string = language.comment_format.format(
                    content=f"Copyright (c) {THIS_YEAR} {git_username}"
                )
                expected_content = (
                    "#!/usr/bin/env python3\n"
                    "\n"
                    f"{copyright_string}\n"
                    "\n"
                    f"<file {file} content sentinel>\n"
                )
                expected_stdout = (
                    f"Fixing file `{file}` - added line(s):\n{copyright_string}\n"
                )
                with open(git_repo.workspace / file, "r") as f:
                    output_content = f.read()

                assert_matching(
                    "output content",
                    "expected content",
                    output_content,
                    expected_content,
                )
                assert expected_stdout in process.stdout


class TestCustomBehaviour:
    class TestConfigFiles:
        class TestGlobalConfigs:
            @staticmethod
            @pytest.mark.parametrize(
                "config_file, config_file_content",
                [
                    (
                        "pyproject.toml",
                        '[tool.add_copyright]\nname="<config file username sentinel>"\n',  # noqa: E501
                    ),
                    (
                        "setup.cfg",
                        "[tool.add_copyright]\nname=<config file username sentinel>\n",
                    ),
                ],
            )
            def test_custom_name_option_overrules_git_username(
                cwd,
                config_file: str,
                config_file_content: str,
                git_repo: GitRepo,
            ):
                # GIVEN
                add_changed_files(
                    [
                        f"hello{lang.extension}"
                        for lang in CopyrightGlobals.SUPPORTED_LANGUAGES
                    ],
                    "",
                    git_repo,
                )
                write_config_file(git_repo.workspace, config_file, config_file_content)

                # WHEN
                with cwd(git_repo.workspace):
                    process: subprocess.CompletedProcess = subprocess.run(
                        COMMAND, capture_output=True, text=True
                    )

                # THEN
                assert process.returncode == 1, process.stdout + process.stderr
                for language in CopyrightGlobals.SUPPORTED_LANGUAGES:
                    file = "hello" + language.extension
                    copyright_string = language.comment_format.format(
                        content=f"Copyright (c) {THIS_YEAR} <config file username sentinel>"  # noqa: E501
                    )
                    expected_content = f"{copyright_string}\n"
                    expected_stdout = (
                        f"Fixing file `{file}` - added line(s):\n{copyright_string}\n"
                    )
                    with open(git_repo.workspace / file, "r") as f:
                        output_content = f.read()

                    assert_matching(
                        "output content",
                        "expected content",
                        output_content,
                        expected_content,
                    )
                    assert expected_stdout in process.stdout

            @staticmethod
            @pytest.mark.parametrize(
                "config_file, config_file_content, expected_copyright_string",
                [
                    (
                        "pyproject.toml",
                        '[tool.add_copyright]\nformat="(C) {name} {year}"\n',
                        "(C) <git config username sentinel> {year}",
                    ),
                    (
                        "setup.cfg",
                        "[tool.add_copyright]\nformat=(C) {name} {year}\n",
                        "(C) <git config username sentinel> {year}",
                    ),
                ],
            )
            def test_custom_format_option_overrules_default_format(
                cwd,
                config_file: str,
                config_file_content: str,
                expected_copyright_string: str,
                git_repo: GitRepo,
            ):
                # GIVEN
                add_changed_files(
                    [
                        f"hello{lang.extension}"
                        for lang in CopyrightGlobals.SUPPORTED_LANGUAGES
                    ],
                    "",
                    git_repo,
                )
                write_config_file(git_repo.workspace, config_file, config_file_content)

                # WHEN
                with cwd(git_repo.workspace):
                    process: subprocess.CompletedProcess = subprocess.run(
                        COMMAND, capture_output=True, text=True
                    )

                # THEN
                assert process.returncode == 1, process.stdout + process.stderr
                for language in CopyrightGlobals.SUPPORTED_LANGUAGES:
                    file = "hello" + language.extension
                    copyright_string = language.comment_format.format(
                        content=expected_copyright_string.format(year=THIS_YEAR)
                    )
                    expected_content = f"{copyright_string}\n"
                    expected_stdout = (
                        f"Fixing file `{file}` - added line(s):\n{copyright_string}\n"
                    )

                    with open(git_repo.workspace / file, "r") as f:
                        output_content = f.read()

                    assert_matching(
                        "output content",
                        "expected content",
                        output_content,
                        expected_content,
                    )
                    assert expected_stdout in process.stdout

        class TestPerLanguageConfigs:
            @staticmethod
            def test_custom_formatting_commented(cwd, git_repo: GitRepo):
                # GIVEN
                add_changed_files(
                    [
                        f"hello{lang.extension}"
                        for lang in CopyrightGlobals.SUPPORTED_LANGUAGES
                    ],
                    "",
                    git_repo,
                )

                toml_text = "\n".join(
                    [
                        f'[tool.add_copyright.{lang.toml_key}]\nformat="""{lang.custom_copyright_format_commented}"""\n'  # noqa: E501
                        for lang in CopyrightGlobals.SUPPORTED_LANGUAGES
                    ]
                )
                write_config_file(git_repo.workspace, "pyproject.toml", toml_text)

                # WHEN
                with cwd(git_repo.workspace):
                    process: subprocess.CompletedProcess = subprocess.run(
                        COMMAND, capture_output=True, text=True
                    )

                # THEN
                assert process.returncode == 1, process.stdout + process.stderr
                for language in CopyrightGlobals.SUPPORTED_LANGUAGES:
                    file = "hello" + language.extension
                    copyright_string = (
                        language.custom_copyright_format_commented.format(
                            name="<git config username sentinel>", year=THIS_YEAR
                        )
                    )
                    expected_content = f"{copyright_string}\n"
                    expected_stdout = (
                        f"Fixing file `{file}` - added line(s):\n{copyright_string}\n"
                    )
                    with open(git_repo.workspace / file, "r") as f:
                        output_content = f.read()

                    assert_matching(
                        "output content",
                        "expected content",
                        output_content,
                        expected_content,
                    )
                    assert expected_stdout in process.stdout

            @staticmethod
            def test_custom_formatting_uncommented(cwd, git_repo: GitRepo):
                # GIVEN
                add_changed_files(
                    [
                        f"hello{lang.extension}"
                        for lang in CopyrightGlobals.SUPPORTED_LANGUAGES
                    ],
                    "",
                    git_repo,
                )
                toml_text = ""
                for language in CopyrightGlobals.SUPPORTED_LANGUAGES:
                    toml_text += (
                        f"[tool.add_copyright.{language.toml_key}]\n"
                        f'format="""{language.custom_copyright_format_uncommented}"""\n\n'  # noqa: E501
                    )
                write_config_file(git_repo.workspace, "pyproject.toml", toml_text)

                # WHEN
                with cwd(git_repo.workspace):
                    process: subprocess.CompletedProcess = subprocess.run(
                        COMMAND, capture_output=True, text=True
                    )

                # THEN
                assert process.returncode == 1, process.stdout + process.stderr
                for language in CopyrightGlobals.SUPPORTED_LANGUAGES:
                    file = "hello" + language.extension
                    copyright_string = language.comment_format.format(
                        content=language.custom_copyright_format_uncommented.format(
                            name="<git config username sentinel>", year=THIS_YEAR
                        )
                    )
                    expected_content = f"{copyright_string}\n"
                    expected_stdout = (
                        f"Fixing file `{file}` - added line(s):\n{copyright_string}\n"
                    )
                    with open(git_repo.workspace / file, "r") as f:
                        output_content = f.read()

                    assert_matching(
                        "output content",
                        "expected content",
                        output_content,
                        expected_content,
                    )
                    assert expected_stdout in process.stdout


class TestFailureStates:
    class TestConfigFailures:
        @staticmethod
        @pytest.mark.parametrize(
            "config_file_content",
            [
                '[tool.add_copyright]\nunsupported_option="should not matter"\n',
                '[tool.add_copyright.unsupported_option]\nname="foo"\n',
            ],
        )
        def test_unsupported_config_options(
            cwd, config_file_content: str, git_repo: GitRepo
        ):
            # GIVEN
            add_changed_files("hello.py", "", git_repo)
            config_file = write_config_file(
                git_repo.workspace, "pyproject.toml", config_file_content
            )

            # WHEN
            with cwd(git_repo.workspace):
                process: subprocess.CompletedProcess = subprocess.run(
                    COMMAND, capture_output=True, text=True
                )

            # THEN
            assert process.returncode == 1, process.stdout + process.stderr
            expected_stdout = (
                'KeyError: "Unsupported option in config file '
                + (str(Path("/private")) if "/private" in process.stdout else "")
                + f"{config_file}: 'unsupported_option'. "
                "Supported options are: "
                f'{CopyrightGlobals.SUPPORTED_TOP_LEVEL_CONFIG_OPTIONS}."'
            )
            assert expected_stdout in process.stdout

        @staticmethod
        @pytest.mark.parametrize(
            "config_file_content",
            [
                '[tool.add_copyright.{language}]\nunsupported_option="should not matter"\n',  # noqa: E501
            ],
        )
        @pytest.mark.parametrize("language", CopyrightGlobals.SUPPORTED_LANGUAGES)
        def test_unsupported_language_config_options(
            cwd,
            config_file_content: str,
            git_repo: GitRepo,
            language: SupportedLanguage,
        ):
            # GIVEN
            add_changed_files("hello.py", "", git_repo)
            write_config_file(
                git_repo.workspace,
                "pyproject.toml",
                config_file_content.format(language=language.toml_key),
            )

            # GIVEN
            file = "hello.py"
            (git_repo.workspace / file).write_text("")
            git_repo.run(f"git add {file}")

            # WHEN
            with cwd(git_repo.workspace):
                process: subprocess.CompletedProcess = subprocess.run(
                    COMMAND, capture_output=True, text=True
                )

            # THEN
            assert process.returncode == 1, process.stdout + process.stderr
            expected_error_string: str = (
                'KeyError: "Unsupported option in config file '
                + (str(Path("/private")) if "/private" in process.stdout else "")
                + f"{git_repo.workspace / 'pyproject.toml'}: "
                f"'{language.toml_key}.unsupported_option'. "
                f"Supported options for '{language.toml_key}' are: "
                f'{CopyrightGlobals.SUPPORTED_PER_LANGUAGE_CONFIG_OPTIONS}."'
            )
            assert expected_error_string in process.stdout, process.stdout

        @staticmethod
        @pytest.mark.parametrize(
            "input_format, missing_keys",
            [
                ("copyright 1996 {name}", "year"),
                ("copyright {year} Harold Hadrada", "name"),
            ],
        )
        @pytest.mark.parametrize("language", CopyrightGlobals.SUPPORTED_LANGUAGES)
        def test_missing_custom_format_keys(
            cwd,
            git_repo: GitRepo,
            input_format: str,
            language: SupportedLanguage,
            missing_keys: str,
        ):
            # GIVEN
            add_changed_files(f"hello{language.extension}", "", git_repo)
            write_config_file(
                git_repo.workspace,
                "pyproject.toml",
                f'[tool.add_copyright.{language.toml_key}]\nformat="{input_format}"\n',
            )

            # WHEN
            with cwd(git_repo.workspace):
                process: subprocess.CompletedProcess = subprocess.run(
                    COMMAND, capture_output=True, text=True
                )

            # THEN
            assert process.returncode == 1, process.stdout + process.stderr
            expected_stdout = f"KeyError: \"The format string '{input_format}' is missing the following required keys: ['{missing_keys}']\""  # noqa: E501
            print("E:", expected_stdout)
            print("R:", process.stdout)
            assert expected_stdout in process.stdout

    class TestInputFileFailures:
        @staticmethod
        @pytest.mark.parametrize("language", CopyrightGlobals.SUPPORTED_LANGUAGES)
        @pytest.mark.parametrize(
            "copyright_string, error_message",
            CopyrightGlobals.INVALID_COPYRIGHT_STRINGS,
        )
        def test_raises_error_for_invalid_copyright_string(
            cwd,
            git_repo: GitRepo,
            copyright_string: str,
            error_message: str,
            language: SupportedLanguage,
        ):
            # GIVEN
            add_changed_files(
                "hello" + language.extension,
                (
                    language.comment_format.format(content=copyright_string)
                    + "\n\n<file content sentinel>"
                ),
                git_repo,
            )

            # WHEN
            with cwd(git_repo.workspace):
                process: subprocess.CompletedProcess = subprocess.run(
                    COMMAND, capture_output=True, text=True
                )

            # THEN
            assert process.returncode == 1, process.stdout + process.stderr
            assert error_message in process.stdout

        @staticmethod
        def test_raises_error_for_invalid_toml(
            cwd,
            git_repo: GitRepo,
        ):
            # GIVEN
            add_changed_files(
                "hello" + CopyrightGlobals.SUPPORTED_LANGUAGES[0].extension,
                "",
                git_repo,
            )
            write_config_file(
                git_repo.workspace,
                "pyproject.toml",
                "[not]valid\ntoml",
            )

            # WHEN
            with cwd(git_repo.workspace):
                process: subprocess.CompletedProcess = subprocess.run(
                    COMMAND, capture_output=True, text=True
                )

            # THEN
            assert process.returncode == 1, process.stdout + process.stderr
            assert (
                "src._shared.exceptions.InvalidConfigError: Could not parse config file "  # noqa: E501
                in process.stdout
            )

        @staticmethod
        def test_raises_error_for_multiple_copyright_strings(
            cwd,
            git_repo: GitRepo,
        ):
            # GIVEN
            copyright_string = CopyrightGlobals.SUPPORTED_LANGUAGES[
                0
            ].comment_format.format(content="Copyright 1312 NAME")
            add_changed_files(
                f"hello{CopyrightGlobals.SUPPORTED_LANGUAGES[0].extension}",
                f"{copyright_string}\n{copyright_string}",
                git_repo,
            )

            # WHEN
            with cwd(git_repo.workspace):
                process: subprocess.CompletedProcess = subprocess.run(
                    COMMAND, capture_output=True, text=True
                )

            # THEN
            assert process.returncode == 1, process.stdout + process.stderr
            assert "ValueError: Found multiple copyright strings: " in process.stdout
