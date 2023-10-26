# Copyright (c) 2023 Benjamin Mummery

import pytest
from pytest import CaptureFixture
from pytest_git import GitRepo
from pytest_mock import MockerFixture

from src.sort_file_contents_hook import sort_file_contents
from tests.conftest import add_changed_files, assert_matching


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
        "file_contents",
        [
            "Alpha\nBeta\nGamma",
            "A\nC\nE\n\nB\nD\nF",
            "# leading comment with clashing entry\n# beta\nbeta\ndelta\nzulu\n",
        ],
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
        "unsorted, sorted, description",
        [
            (
                "beta\ndelta\ngamma\nalpha\n",
                "alpha\nbeta\ndelta\ngamma\n",
                "no sections",
            ),
            (
                "beta\ndelta\n\ngamma\nalpha\n",
                "beta\ndelta\n\nalpha\ngamma\n",
                "sections",
            ),
            (
                "# zulu\nbeta\ndelta\ngamma\nalpha\n",
                "# zulu\nalpha\nbeta\ndelta\ngamma\n",
                "leading comment, no sections",
            ),
            (
                "# zulu\n# alpha\nbeta\ngamma\ndelta\n",
                "# zulu\n# alpha\nbeta\ndelta\ngamma\n",
                "multiline leading comment, no sections",
            ),
            (
                "# zulu\nbeta\ndelta\n\n# epsilon\ngamma\nalpha\n",
                "# zulu\nbeta\ndelta\n\n# epsilon\nalpha\ngamma\n",
                "multiple sections with leading comment",
            ),
            (
                "beta\n# zulu\ndelta\ngamma\nalpha\n",
                "alpha\nbeta\ndelta\ngamma\n# zulu\n",
                "commented line within section - sort to end",
            ),
            (
                "beta\nzulu\n# delta\ngamma\nalpha\n",
                "alpha\nbeta\n# delta\ngamma\nzulu\n",
                "commented line within section - sort to middle",
            ),
            (
                "beta\ndelta\n\n# zulu\n\ngamma\nalpha\n",
                "beta\ndelta\n\n# zulu\n\nalpha\ngamma\n",
                "floating comment",
            ),
            (
                "beta\ndelta\nbeta\n\ngamma\nalpha\ngamma\n",
                "beta\nbeta\ndelta\n\nalpha\ngamma\ngamma\n",
                "duplicates within sections",
            ),
            (
                "beta\ndelta\n\ngamma\nalpha\ndelta\n",
                "beta\ndelta\n\nalpha\ndelta\ngamma\n",
                "duplicates between sections",
            ),
            (
                "beta\ndelta\n\n\ngamma\nalpha\n",
                "beta\ndelta\n\nalpha\ngamma\n",
                "double linebreak between sections",
            ),
        ],
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
        assert_matching("captured stderr", "expected stderr", captured.err, "")

    @staticmethod
    @pytest.mark.parametrize("unique_flag", ["-u", "--unique"])
    @pytest.mark.parametrize(
        "unsorted, sorted, description",
        [
            (
                "beta\ndelta\ngamma\nalpha\ndelta\n",
                "alpha\nbeta\ndelta\ngamma\n",
                "no sections",
            ),
            (
                "beta\ndelta\nbeta\n\ngamma\nalpha\nalpha\n",
                "beta\ndelta\n\nalpha\ngamma\n",
                "sections",
            ),
            (
                "# zulu\nbeta\ndelta\ngamma\nalpha\ngamma\n",
                "# zulu\nalpha\nbeta\ndelta\ngamma\n",
                "leading comment, no sections",
            ),
            (
                "# zulu\nbeta\ndelta\ndelta\n\n# epsilon\ngamma\nalpha\n",
                "# zulu\nbeta\ndelta\n\n# epsilon\nalpha\ngamma\n",
                "multiple sections with leading comment",
            ),
            (
                "beta\ndelta\n# zulu\n# zulu\n",
                "beta\ndelta\n# zulu\n",
                "duplicate comments",
            ),
        ],
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
            message="Failed to sort file with {description}.",
        )
        captured = capsys.readouterr()
        assert_matching(
            "captured stdout",
            "expected stdout",
            captured.out,
            f"Sorting file '{filename}'\n",
        )
        assert_matching("captured stderr", "expected stderr", captured.err, "")


class TestFailureStates:
    @staticmethod
    @pytest.mark.parametrize("unique_flag", ["-u", "--unique"])
    @pytest.mark.parametrize("unsorted", ["beta\ndelta\n\ngamma\nalpha\ndelta\n"])
    def test_duplicates_between_sections_with_unique_flag(
        cwd,
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
            "src.sort_file_contents_hook.sort_file_contents.UnsortableError: Could not sort '.gitignore'. The following entries appear in multiple sections:\n- 'delta' appears in 2 sections.",  # noqa: E501
        )

    @staticmethod
    @pytest.mark.parametrize("unique_flag", ["-u", "--unique"])
    @pytest.mark.parametrize(
        "unsorted, clashing_entry, description",
        [
            ("beta\n# zulu\ndelta\ngamma\nalpha\nzulu\n", "zulu", "simple clash"),
            (
                "# leading comment\n# zulu\n# including clash\nalpha\n# alpha\nzulu",
                "alpha",
                "potential clash in leading comment",
            ),
        ],
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
