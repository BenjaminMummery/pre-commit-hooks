# Copyright (c) 2023 - 2024 Benjamin Mummery

import pytest
from pytest import CaptureFixture
from pytest_git import GitRepo
from pytest_mock import MockerFixture

from conftest import SortFileContentsGlobals, add_changed_files, assert_matching
from src.sort_file_contents_hook import sort_file_contents


@pytest.mark.usefixtures("git_repo")
class TestNoChanges:
    @staticmethod
    def test_no_files_changed(
        capsys: CaptureFixture,
        cwd,
        mocker: MockerFixture,
        git_repo: GitRepo,
    ):
        # GIVEN
        mocker.patch("sys.argv", ["stub_name"])

        # WHEN
        with cwd(git_repo.workspace):
            assert sort_file_contents.main() == 0

        # THEN
        captured = capsys.readouterr()
        assert_matching("captured stdout", "expected stdout", captured.out, "")
        assert_matching("captured stderr", "expected stderr", captured.err, "")

    @staticmethod
    @pytest.mark.parametrize(
        "file_contents", SortFileContentsGlobals.SORTED_FILE_CONTENTS
    )
    def test_all_changed_files_are_sorted(
        capsys: CaptureFixture,
        cwd,
        file_contents: str,
        mocker: MockerFixture,
        git_repo: GitRepo,
    ):
        # GIVEN
        add_changed_files(".gitignore", file_contents, git_repo, mocker)

        # WHEN
        with cwd(git_repo.workspace):
            assert sort_file_contents.main() == 0

        # THEN
        with open(git_repo.workspace / ".gitignore", "r") as f:
            content = f.read()
        assert_matching(
            "output file contents", "expected file contents", content, file_contents
        )
        captured = capsys.readouterr()
        assert_matching("captured stdout", "expected stdout", captured.out, "")
        assert_matching("captured stderr", "expected stderr", captured.err, "")

    @staticmethod
    def test_empty_file(
        capsys: CaptureFixture,
        cwd,
        mocker: MockerFixture,
        git_repo: GitRepo,
    ):
        # GIVEN
        add_changed_files(".gitignore", "", git_repo, mocker)

        # WHEN
        with cwd(git_repo.workspace):
            assert sort_file_contents.main() == 0

        # THEN
        with open(git_repo.workspace / ".gitignore", "r") as f:
            content = f.read()
        assert_matching("output file contents", "expected file contents", content, "")
        captured = capsys.readouterr()
        assert_matching("captured stdout", "expected stdout", captured.out, "")
        assert_matching("captured stderr", "expected stderr", captured.err, "")


@pytest.mark.usefixtures("git_repo")
class TestSorting:
    @staticmethod
    @pytest.mark.parametrize(
        "unsorted, sorted, description", SortFileContentsGlobals.UNSORTED_FILE_CONTENTS
    )
    def test_default_file_sorting(
        capsys: CaptureFixture,
        cwd,
        mocker: MockerFixture,
        git_repo: GitRepo,
        unsorted: str,
        sorted: str,
        description: str,
    ):
        # GIVEN
        add_changed_files(filename := ".gitignore", unsorted, git_repo, mocker)

        # WHEN
        with cwd(git_repo.workspace):
            assert sort_file_contents.main() == 1

        # THEN
        with open(git_repo.workspace / filename, "r") as f:
            content = f.read()
        assert_matching(
            "output file contents",
            "expected file contents",
            content,
            sorted,
            message="Failed to sort file with {description}.",
        )
        captured = capsys.readouterr()
        assert_matching(
            "captured stdout",
            "expected stdout",
            captured.out,
            f"Sorting file '{filename}'\n",
        )
        assert_matching(
            "captured stderr", "expected stderr", captured.err, "", message=description
        )

    @staticmethod
    @pytest.mark.parametrize("unique_flag", ["-u", "--unique"])
    @pytest.mark.parametrize(
        "unsorted, sorted, description",
        SortFileContentsGlobals.DUPLICATES_WITHIN_SECTIONS_FILE_CONTENTS,
    )
    def test_sorting_unique(
        capsys: CaptureFixture,
        cwd,
        mocker: MockerFixture,
        git_repo: GitRepo,
        unsorted: str,
        sorted: str,
        description: str,
        unique_flag: str,
    ):
        # GIVEN
        add_changed_files(filename := ".gitignore", unsorted, git_repo, mocker)
        mocker.patch("sys.argv", ["stub_name", unique_flag, filename])

        # WHEN
        with cwd(git_repo.workspace):
            assert sort_file_contents.main() == 1

        # THEN
        with open(git_repo.workspace / filename, "r") as f:
            content = f.read()
        assert_matching(
            "output file contents",
            "expected file contents",
            content,
            sorted,
            message=f"Failed to sort file with {description}.",
        )
        captured = capsys.readouterr()
        assert_matching(
            "captured stdout",
            "expected stdout",
            captured.out,
            f"Sorting file '{filename}'\n",
            message=description,
        )
        assert_matching(
            "captured stderr", "expected stderr", captured.err, "", message=description
        )


class TestFailureStates:
    @staticmethod
    @pytest.mark.parametrize("unique_flag", ["-u", "--unique"])
    @pytest.mark.parametrize(
        "unsorted, clashing_entry, description",
        SortFileContentsGlobals.DUPLICATES_BETWEEN_SECTIONS_FILE_CONTENTS,
    )
    def test_duplicates_between_sections_with_unique_flag(
        cwd,
        clashing_entry: str,
        description: str,
        mocker: MockerFixture,
        git_repo: GitRepo,
        unsorted: str,
        unique_flag: str,
    ):
        # GIVEN
        add_changed_files(filename := ".gitignore", unsorted, git_repo, mocker)
        mocker.patch("sys.argv", ["stub_name", unique_flag, filename])

        # WHEN
        with cwd(git_repo.workspace):
            with pytest.raises(sort_file_contents.UnsortableError) as e:
                sort_file_contents.main()

        # THEN
        with open(git_repo.workspace / filename, "r") as f:
            content = f.read()
        assert_matching(
            "output file contents", "expected file contents", content, unsorted
        )
        assert_matching(
            "Captured error message",
            "Expected error message",
            e.exconly(),
            f"src.sort_file_contents_hook.sort_file_contents.UnsortableError: Could not sort '.gitignore'. The following entries appear in multiple sections:\n- '{clashing_entry}' appears in 2 sections.",  # noqa: E501
            message=description,
        )

    @staticmethod
    @pytest.mark.parametrize("unique_flag", ["-u", "--unique"])
    @pytest.mark.parametrize(
        "unsorted, clashing_entry, description",
        SortFileContentsGlobals.COMMENTED_AND_UNCOMMENTED_DUPLICATES,
    )
    def test_commented_and_uncommented_duplicates(
        cwd,
        clashing_entry: str,
        description: str,
        mocker: MockerFixture,
        git_repo: GitRepo,
        unsorted: str,
        unique_flag: str,
    ):
        # GIVEN
        add_changed_files(filename := ".gitignore", unsorted, git_repo, mocker)
        mocker.patch("sys.argv", ["stub_name", unique_flag, filename])

        # WHEN
        with cwd(git_repo.workspace):
            with pytest.raises(sort_file_contents.UnsortableError) as e:
                sort_file_contents.main()

        # THEN
        with open(git_repo.workspace / filename, "r") as f:
            content = f.read()
        assert_matching(
            "output file contents", "expected file contents", content, unsorted
        )
        assert_matching(
            "Captured error message",
            "Expected error message",
            e.exconly(),
            f"src.sort_file_contents_hook.sort_file_contents.UnsortableError: Could not sort '{filename}'. The following entries exists in both commented and uncommented forms:\n- '{clashing_entry}'.",  # noqa: E501
            message=description,
        )

    @staticmethod
    def test_missing_file(
        cwd,
        mocker: MockerFixture,
        git_repo: GitRepo,
    ):
        # GIVEN
        mocker.patch("sys.argv", ["stub_name", filename := "file_does_not_exist"])

        # WHEN
        with cwd(git_repo.workspace):
            with pytest.raises(FileNotFoundError) as e:
                sort_file_contents.main()

        # THEN
        assert_matching(
            "Captured error message",
            "Expected error message",
            e.exconly(),
            f"FileNotFoundError: {filename}",
        )
