# Copyright (c) 2023 - 2026 Benjamin Mummery
from pathlib import Path

import pytest

from freezegun import freeze_time
from pytest import CaptureFixture
from pytest_git import GitRepo
from pytest_mock import MockerFixture

from conftest import (
    CopyrightGlobals,
    SupportedLanguage,
    add_changed_files,
    assert_matching,
)
from src.update_copyright_hook import update_copyright


@pytest.fixture(autouse=True)
def mock_commit_year_range(mocker):
    return mocker.patch(
        "src.update_copyright_hook.update_copyright._get_commit_year_range",
        return_value=(1312, 1312),
    )


@pytest.fixture()
def mock_colour(mocker):
    mocker.patch(
        "src.update_copyright_hook.update_copyright.print_diff.REMOVED_COLOUR",
        "",
    )
    mocker.patch(
        "src.update_copyright_hook.update_copyright.print_diff.ADDED_COLOUR",
        "",
    )
    mocker.patch(
        "src.update_copyright_hook.update_copyright.print_diff.END_COLOUR",
        "",
    )


@pytest.mark.usefixtures("git_repo")
class TestNoChanges:
    @staticmethod
    def test_reads_committer_year_range_from_git_history(
        mock_commit_year_range,
        mocker: MockerFixture,
    ):
        # GIVEN
        mocker.stop(mock_commit_year_range)
        repo = mocker.patch(
            "src.update_copyright_hook.update_copyright.Repo",
        ).return_value
        repo.git.log.return_value = "1312-01-01\n1066-12-31\n1088-06-01"

        # WHEN / THEN
        assert update_copyright._get_commit_year_range(
            Path("hello.py"),
            "revision-sentinel",
        ) == (1066, 1312)
        repo.git.log.assert_called_once_with(
            "revision-sentinel",
            "--follow",
            "--format=%cs",
            "--",
            "hello.py",
        )

    @staticmethod
    def test_rejects_a_pushed_revision_other_than_checked_out_head(
        mocker: MockerFixture,
    ):
        # GIVEN
        mocker.patch("sys.argv", ["stub_name"])
        mocker.patch.dict("os.environ", {"PRE_COMMIT_TO_REF": "pushed-ref"})
        repo = mocker.patch(
            "src.update_copyright_hook.update_copyright.Repo",
        ).return_value
        repo.head.commit.hexsha = "checked-out-head"
        repo.commit.return_value.hexsha = "pushed-head"

        # WHEN / THEN
        with pytest.raises(RuntimeError) as e:
            update_copyright.main()
        assert "can only modify the checked-out revision" in e.exconly()

    @staticmethod
    def test_no_files_changed(
        capsys: CaptureFixture,
        mocker: MockerFixture,
    ):
        # GIVEN
        mocker.patch("sys.argv", ["stub_name"])

        # WHEN
        assert update_copyright.main() == 0

        # THEN
        captured = capsys.readouterr()
        assert_matching("captured stdout", "expected stdout", captured.out, "")
        assert_matching("captured stderr", "expected stderr", captured.err, "")

    @staticmethod
    @freeze_time("1312-01-01")
    @pytest.mark.parametrize("language", CopyrightGlobals.SUPPORTED_LANGUAGES)
    @pytest.mark.parametrize(
        "copyright_string",
        [s.format(end_year="1312") for s in CopyrightGlobals.VALID_COPYRIGHT_STRINGS],
    )
    def test_all_changed_files_have_current_copyright_comment(
        capsys: CaptureFixture,
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
            assert update_copyright.main() == 0

        # THEN
        # Gather actual outputs
        with open(git_repo.workspace / file) as f:
            output_content = f.read()
        captured = capsys.readouterr()

        # Compare
        assert_matching(
            "output content",
            "expected content",
            output_content,
            file_content,
        )
        assert_matching("captured stdout", "expected stdout", captured.out, "")
        assert_matching("captured stderr", "expected stderr", captured.err, "")

    @staticmethod
    @freeze_time("1312-01-01")
    @pytest.mark.parametrize("language", CopyrightGlobals.DOCSTR_SUPPORTED_LANGUAGES)
    @pytest.mark.parametrize(
        "copyright_string",
        [s.format(end_year="1312") for s in CopyrightGlobals.VALID_COPYRIGHT_STRINGS],
    )
    def test_all_changed_files_have_current_copyright_docstring(
        capsys: CaptureFixture,
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
                f'"""\n{copyright_string}\n"""\n\n<file content sentinel>'
            ),
            git_repo,
            mocker,
        )

        # WHEN
        with cwd(git_repo.workspace):
            assert update_copyright.main() == 0

        # THEN
        # Gather actual outputs
        with open(git_repo.workspace / file) as f:
            output_content = f.read()
        captured = capsys.readouterr()

        # Compare
        assert_matching(
            "output content",
            "expected content",
            output_content,
            file_content,
        )
        assert_matching("captured stdout", "expected stdout", captured.out, "")
        assert_matching("captured stderr", "expected stderr", captured.err, "")

    @staticmethod
    @freeze_time("1312-01-01")
    @pytest.mark.parametrize("language", CopyrightGlobals.SUPPORTED_LANGUAGES)
    def test_no_changed_files_have_copyright(
        capsys: CaptureFixture,
        cwd,
        git_repo: GitRepo,
        language: SupportedLanguage,
        mocker: MockerFixture,
    ):
        # GIVEN
        add_changed_files(
            file := "hello" + language.extension,
            file_content := "<file content sentinel>\n",
            git_repo,
            mocker,
        )

        # WHEN
        with cwd(git_repo.workspace):
            assert update_copyright.main() == 0

        # THEN
        # Gather actual outputs
        with open(git_repo.workspace / file) as f:
            output_content = f.read()
        captured = capsys.readouterr()

        # Compare
        assert_matching(
            "output content",
            "expected content",
            output_content,
            file_content,
        )
        assert_matching("captured stdout", "expected stdout", captured.out, "")
        assert_matching("captured stderr", "expected stderr", captured.err, "")


class TestChanges:
    @staticmethod
    def test_extends_both_ends_of_range_from_history(
        cwd,
        git_repo: GitRepo,
        mock_commit_year_range,
        mocker: MockerFixture,
    ):
        # GIVEN
        mock_commit_year_range.return_value = (1066, 1312)
        add_changed_files(
            file := "hello.py",
            "# Copyright 1088 - 1300 NAME\n",
            git_repo,
            mocker,
        )

        # WHEN
        with cwd(git_repo.workspace):
            assert update_copyright.main() == 1

        # THEN
        assert (git_repo.workspace / file).read_text() == (
            "# Copyright 1066 - 1312 NAME\n"
        )

    @staticmethod
    def test_never_shortens_declared_range(
        cwd,
        git_repo: GitRepo,
        mock_commit_year_range,
        mocker: MockerFixture,
    ):
        # GIVEN
        mock_commit_year_range.return_value = (1088, 1300)
        content = "# Copyright 1066-1312 NAME\n"
        add_changed_files(file := "hello.py", content, git_repo, mocker)

        # WHEN
        with cwd(git_repo.workspace):
            assert update_copyright.main() == 0

        # THEN
        assert (git_repo.workspace / file).read_text() == content

    @staticmethod
    @pytest.mark.parametrize("language", CopyrightGlobals.SUPPORTED_LANGUAGES)
    @pytest.mark.parametrize(
        "input_copyright_string, expected_copyright_string",
        [
            ("Copyright 1066 NAME", "Copyright 1066-1312 NAME"),
            ("Copyright (c) 1066 NAME", "Copyright (c) 1066-1312 NAME"),
            ("(c) 1066 NAME", "(c) 1066-1312 NAME"),
        ],
    )
    @freeze_time("1312-01-01")
    def test_updates_single_date_copyright_comments(
        capsys: CaptureFixture,
        cwd,
        expected_copyright_string: str,
        git_repo: GitRepo,
        input_copyright_string: str,
        language: SupportedLanguage,
        mocker: MockerFixture,
        mock_colour,
    ):
        # GIVEN
        add_changed_files(
            file := "hello" + language.extension,
            language.comment_format.format(content=input_copyright_string)
            + "\n\n<file content sentinel>",
            git_repo,
            mocker,
        )

        # WHEN
        with cwd(git_repo.workspace):
            assert update_copyright.main() == 1

        # THEN
        # Construct expected outputs
        new_copyright_string = language.comment_format.format(
            content=expected_copyright_string,
        )
        expected_content = f"{new_copyright_string}\n\n<file content sentinel>"
        expected_stdout = (
            f"Fixing file `{file}`:\n"
            f"  - {language.comment_format.format(content=input_copyright_string)}\n"
            f"  + {new_copyright_string}\n"
        )

        # Gather actual outputs
        with open(git_repo.workspace / file) as f:
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
            "captured stdout",
            "expected stdout",
            captured.out,
            expected_stdout,
        )
        assert_matching("captured stderr", "expected stderr", captured.err, "")

    @staticmethod
    @pytest.mark.parametrize("language", CopyrightGlobals.SUPPORTED_LANGUAGES)
    @pytest.mark.parametrize(
        "input_copyright_string, expected_copyright_string",
        [
            ("Copyright 1066 - 1088 NAME", "Copyright 1066 - 1312 NAME"),
            ("Copyright (c) 1066-1088 NAME", "Copyright (c) 1066-1312 NAME"),
        ],
    )
    @freeze_time("1312-01-01")
    def test_updates_multiple_date_copyrights(
        capsys: CaptureFixture,
        cwd,
        expected_copyright_string: str,
        git_repo: GitRepo,
        input_copyright_string: str,
        language: SupportedLanguage,
        mocker: MockerFixture,
        mock_colour,
    ):
        # GIVEN
        add_changed_files(
            file := "hello" + language.extension,
            language.comment_format.format(content=input_copyright_string)
            + "\n\n<file content sentinel>",
            git_repo,
            mocker,
        )

        # WHEN
        with cwd(git_repo.workspace):
            assert update_copyright.main() == 1

        # THEN
        # Construct expected outputs
        new_copyright_string = language.comment_format.format(
            content=expected_copyright_string,
        )
        expected_content = f"{new_copyright_string}\n\n<file content sentinel>"
        expected_stdout = (
            f"Fixing file `{file}`:\n"
            f"  - {language.comment_format.format(content=input_copyright_string)}\n"
            f"  + {new_copyright_string}\n"
        )

        # Gather actual outputs
        with open(git_repo.workspace / file) as f:
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
            "captured stdout",
            "expected stdout",
            captured.out,
            expected_stdout,
        )
        assert_matching("captured stderr", "expected stderr", captured.err, "")

    @staticmethod
    @pytest.mark.parametrize("language", CopyrightGlobals.DOCSTR_SUPPORTED_LANGUAGES)
    @pytest.mark.parametrize(
        "input_copyright_string, expected_copyright_string",
        [
            ("Copyright 1066 NAME", "Copyright 1066-1312 NAME"),
            ("Copyright (c) 1066 NAME", "Copyright (c) 1066-1312 NAME"),
            ("(c) 1066 NAME", "(c) 1066-1312 NAME"),
        ],
    )
    @freeze_time("1312-01-01")
    def test_updates_single_date_copyright_docstrings(
        capsys: CaptureFixture,
        cwd,
        expected_copyright_string: str,
        git_repo: GitRepo,
        input_copyright_string: str,
        language: SupportedLanguage,
        mocker: MockerFixture,
        mock_colour,
    ):
        # GIVEN
        file_content = "def foo():\n    pass"
        add_changed_files(
            file := "hello" + language.extension,
            f'"""\n{input_copyright_string}\n"""\n\n{file_content}',
            git_repo,
            mocker,
        )

        # WHEN
        with cwd(git_repo.workspace):
            assert update_copyright.main() == 1

        # THEN
        # Construct expected outputs
        expected_content = f'"""\n{expected_copyright_string}\n"""\n\n{file_content}'
        expected_stdout = (
            f"Fixing file `{file}`:\n"
            f"  - {input_copyright_string}\n"
            f"  + {expected_copyright_string}\n"
        )

        # Gather actual outputs
        with open(git_repo.workspace / file) as f:
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
            "captured stdout",
            "expected stdout",
            captured.out,
            expected_stdout,
        )
        assert_matching("captured stderr", "expected stderr", captured.err, "")

    @staticmethod
    @pytest.mark.parametrize("language", CopyrightGlobals.DOCSTR_SUPPORTED_LANGUAGES)
    @pytest.mark.parametrize(
        "input_copyright_string, expected_copyright_string",
        [
            ("Copyright 1066 - 1088 NAME", "Copyright 1066 - 1312 NAME"),
            ("Copyright (c) 1066-1088 NAME", "Copyright (c) 1066-1312 NAME"),
        ],
    )
    @freeze_time("1312-01-01")
    def test_updates_multiple_date_copyright_docstrings(
        capsys: CaptureFixture,
        cwd,
        expected_copyright_string: str,
        git_repo: GitRepo,
        input_copyright_string: str,
        language: SupportedLanguage,
        mocker: MockerFixture,
        mock_colour,
    ):
        # GIVEN
        file_content = "def foo():\n    pass"
        add_changed_files(
            file := "hello" + language.extension,
            f'"""\n{input_copyright_string}\n"""\n\n{file_content}',
            git_repo,
            mocker,
        )

        # WHEN
        with cwd(git_repo.workspace):
            assert update_copyright.main() == 1

        # THEN
        # Construct expected outputs
        expected_content = f'"""\n{expected_copyright_string}\n"""\n\n{file_content}'
        expected_stdout = (
            f"Fixing file `{file}`:\n"
            f"  - {input_copyright_string}\n"
            f"  + {expected_copyright_string}\n"
        )

        # Gather actual outputs
        with open(git_repo.workspace / file) as f:
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
            "captured stdout",
            "expected stdout",
            captured.out,
            expected_stdout,
        )
        assert_matching("captured stderr", "expected stderr", captured.err, "")


class TestFailureStates:
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
        mocker: MockerFixture,
        mock_colour,
    ):
        # GIVEN
        add_changed_files(
            "hello" + language.extension,
            (
                language.comment_format.format(content=copyright_string)
                + "\n\n<file content sentinel>"
            ),
            git_repo,
            mocker,
        )

        # WHEN
        with cwd(git_repo.workspace), pytest.raises(ValueError) as e:
            update_copyright.main()

        # THEN
        assert_matching(
            "Output error string",
            "Expected error string",
            e.exconly(),
            error_message,
        )

    @staticmethod
    def test_raises_error_for_invalid_file_format(
        cwd,
        git_repo: GitRepo,
        mocker: MockerFixture,
    ):
        """
        This should never happen in practice since the pre-commit framework should
        prevent non-supported files getting passed in.
        """
        # GIVEN
        add_changed_files("hello.fake", "", git_repo, mocker)

        # WHEN
        with cwd(git_repo.workspace), pytest.raises(NotImplementedError) as e:
            update_copyright.main()

        # THEN
        assert e.exconly().startswith(
            "NotImplementedError: The file extension '.fake' is not currently supported. File has tags: {",  # noqa: E501
        )
