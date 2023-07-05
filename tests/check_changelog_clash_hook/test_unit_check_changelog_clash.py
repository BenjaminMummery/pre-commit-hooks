# Copyright (c) 2023 Benjamin Mummery

from pathlib import Path
from unittest.mock import Mock, call, create_autospec

import git
import pytest
from pytest_mock.plugin import MockerFixture

from src.check_changelog_clash_hook import check_changelog_clash

from ..conftest import CHECK_CHANGELOG_CLASH_FIXTURE_LIST as FIXTURES


@pytest.mark.usefixtures(*[f for f in FIXTURES if f != "mock_check_changelog_clash"])
class TestCheckChangelogClash:
    @staticmethod
    def test_returns_0_for_no_differences(mock_get_changes: Mock):
        # GIVEN
        mock_get_changes.return_value = None

        # WHEN
        ret = check_changelog_clash._check_changelog_clash("<file sentinel>")

        # THEN
        assert ret == 0
        mock_get_changes.assert_called_once_with("<file sentinel>")


@pytest.mark.usefixtures(*[f for f in FIXTURES if f != "mock_get_heading_level"])
class TestGetHeadingLevel:
    @staticmethod
    @pytest.mark.parametrize("input, expected_level", [("# foo", 1), ("## bar", 2)])
    def test_happy_path(input: str, expected_level: int):
        assert check_changelog_clash._get_heading_level(input) == expected_level


@pytest.mark.usefixtures(*[f for f in FIXTURES if f != "mock_parse_subsections"])
class TestParseSubsections:
    @staticmethod
    def test_identifies_level_section_headings(
        mock_get_heading_level: Mock, mock_parse_section: Mock
    ):
        # GIVEN
        mock_get_heading_level.side_effect = [1, 2]
        mock_parse_section.side_effect = [
            "<parsed section sentinel 1>",
            "<parsed section sentinel 2>",
        ]

        # WHEN
        check_changelog_clash._parse_subsections(
            [
                "# <level 1 sentinel>",
                "<non-heading sentinel 1>",
                "## <level 2 sentinel>",
                "<non-heading sentinel 2>",
            ]
        )

        # THEN
        mock_get_heading_level.assert_has_calls(
            [call("# <level 1 sentinel>"), call("## <level 2 sentinel>")]
        )
        assert mock_get_heading_level.call_count == 2
        mock_parse_section.assert_called_once_with(
            [
                "<non-heading sentinel 1>",
                "## <level 2 sentinel>",
                "<non-heading sentinel 2>",
            ],
            1,
        )

    @staticmethod
    def test_with_no_headings(mock_parse_section: Mock):
        """If there are no headings, parse the entire input as a single section."""
        # GIVEN
        mock_parse_section.return_value = "<parsed section sentinel>"
        input = ["<non-heading sentinel 1>", "<non-heading sentinel 2>"]
        # WHEN
        ret = check_changelog_clash._parse_subsections(input)

        # THEN
        assert ret == "<parsed section sentinel>"
        mock_parse_section.assert_called_once_with(input, 0)


@pytest.mark.usefixtures(*[f for f in FIXTURES if f != "mock_parse_section"])
class TestParseSection:
    @staticmethod
    def test_no_subsections(mock_parse_subsections: Mock):
        # GIVEN
        input = ["<line 1 sentinel>", "<line 2 sentinel>", "<line 3 sentinel>"]

        # WHEN
        ret = check_changelog_clash._parse_section(input, Mock())

        # THEN
        assert ret["lines"] == input
        mock_parse_subsections.assert_not_called()

    @staticmethod
    @pytest.mark.parametrize("level", [0, 1, 2, 3, 5, 8, 117, -666])
    def test_level_is_ignored_if_no_subsections(
        mock_parse_subsections: Mock, level: int
    ):
        # GIVEN
        input = ["<line 1 sentinel>", "<line 2 sentinel>", "<line 3 sentinel>"]

        # WHEN
        ret = check_changelog_clash._parse_section(input, level)

        # THEN
        assert ret["lines"] == input

    @staticmethod
    def test_with_subsections(mock_parse_subsections: Mock):
        # GIVEN
        input = [
            "<line 1 sentinel>",
            "## <heading sentinel >",
            "<line 2 sentinel>",
            "<line 3 sentinel>",
        ]
        mock_parse_subsections.return_value = {
            "<parsed heading sentinel>": ["<parsed lien sentinel>"]
        }

        # WHEN
        ret = check_changelog_clash._parse_section(input, 1)

        # THEN
        assert ret["lines"] == ["<line 1 sentinel>"]
        assert "<parsed heading sentinel>" in ret.keys()
        assert ret["<parsed heading sentinel>"] == ["<parsed lien sentinel>"]
        mock_parse_subsections.assert_called_once_with(
            ["## <heading sentinel >", "<line 2 sentinel>", "<line 3 sentinel>"], 2
        )

    @staticmethod
    @pytest.mark.parametrize("level", [0, 1, 2, 3, 5, 8, 117, -666])
    def test_sets_correct_level_for_subsections(
        mock_parse_subsections: Mock, level: int
    ):
        # GIVEN
        input = [
            "<line 1 sentinel>",
            "## <heading sentinel >",
            "<line 2 sentinel>",
            "<line 3 sentinel>",
        ]

        # WHEN
        _ = check_changelog_clash._parse_section(input, level)

        # THEN
        mock_parse_subsections.assert_called_once_with(
            ["## <heading sentinel >", "<line 2 sentinel>", "<line 3 sentinel>"],
            level + 1,
        )


@pytest.mark.usefixtures(*[f for f in FIXTURES if f != "mock_get_changes"])
class TestGetChanges:
    @staticmethod
    def test_early_return_for_no_changes(mocker: MockerFixture):
        # GIVEN
        mock_repo = create_autospec(git.Repo)
        mock_diff_index = create_autospec(git.DiffIndex)
        mock_repo.index.diff.return_value = mock_diff_index
        mocker.patch("git.Repo", return_value=mock_repo)

        # WHEN
        comparison = check_changelog_clash._get_changes("<file sentinel>")

        # THEN
        assert comparison is None
        mock_repo.remotes.origin.fetch.assert_called_once_with()
        mock_repo.index.diff.assert_called_once_with("origin/main", "<file sentinel>")

    @staticmethod
    def test_reports_changes(mocker: MockerFixture, tmp_path: Path):
        # GIVEN
        local_file_contents = "<A sentinel 1>\n<A sentinel 2>"
        remote_file_contents = "<B sentinel 1>\n<B sentinel 2>"

        mock_file = tmp_path / "file.py"
        mock_file.write_text(local_file_contents)

        mock_repo = create_autospec(git.Repo)
        mock_diff = Mock()
        mock_diff.a_blob.data_stream.read.return_value = local_file_contents.encode(
            "utf-8"
        )
        mock_diff.b_blob.data_stream.read.return_value = remote_file_contents.encode(
            "utf-8"
        )
        mock_repo.index.diff.return_value = [mock_diff]
        mocker.patch("git.Repo", return_value=mock_repo)

        # WHEN
        comparison = check_changelog_clash._get_changes(mock_file)

        # THEN
        assert comparison is not None
        assert comparison.local == local_file_contents.splitlines()
        assert comparison.remote == remote_file_contents.splitlines()
        mock_repo.remotes.origin.fetch.assert_called_once_with()
        mock_repo.index.diff.assert_called_once_with("origin/main", mock_file)

    @staticmethod
    def test_raises_AssertionError_for_longer_diff_index(mocker: MockerFixture):
        # GIVEN
        mock_repo = create_autospec(git.Repo)
        mock_diff = Mock()
        mock_repo.index.diff.return_value = [mock_diff, mock_diff]
        mocker.patch("git.Repo", return_value=mock_repo)

        # WHEN
        with pytest.raises(AssertionError):
            _ = check_changelog_clash._get_changes("<file sentinel>")

    @staticmethod
    def test_raises_AssertionError_for_mismatch_with_local_file(
        mocker: MockerFixture, tmp_path: Path
    ):
        # GIVEN
        local_file_contents = "<A sentinel 1>\n<A sentinel 2>"
        remote_file_contents = "<B sentinel 1>\n<B sentinel 2>"

        mock_file = tmp_path / "file.py"
        mock_file.write_text("not local file contents")

        mock_repo = create_autospec(git.Repo)
        mock_diff = Mock()
        mock_diff.a_blob.data_stream.read.return_value = local_file_contents.encode(
            "utf-8"
        )
        mock_diff.b_blob.data_stream.read.return_value = remote_file_contents.encode(
            "utf-8"
        )
        mock_repo.index.diff.return_value = [mock_diff]
        mocker.patch("git.Repo", return_value=mock_repo)

        # WHEN
        with pytest.raises(AssertionError):
            _ = check_changelog_clash._get_changes(mock_file)


@pytest.mark.usefixtures(
    *[f for f in FIXTURES if f != "mock_parse_check_changelog_clash_args"]
)
class TestParseArgs:
    @staticmethod
    @pytest.mark.parametrize(
        "file_arg", [[], ["stub_file"], ["stub_file_1", "stub_file_2"]]
    )
    def test_arg_passing(file_arg, mocker):
        # GIVEN
        mocker.patch("sys.argv", ["stub", *file_arg])

        # WHEN
        args = check_changelog_clash._parse_args()

        # THEN
        assert args.files == file_arg


@pytest.mark.usefixtures(*FIXTURES)
class TestMain:
    @staticmethod
    def test_early_return_for_no_files(
        mock_parse_check_changelog_clash_args, mock_check_changelog_clash
    ):
        # GIVEN
        mock_parse_check_changelog_clash_args.return_value = Mock(files=[])

        # WHEN
        assert check_changelog_clash.main() == 0

        # THEN
        mock_check_changelog_clash.assert_not_called()

    @staticmethod
    def test_returns_1_for_changed_files(
        mock_parse_check_changelog_clash_args, mock_check_changelog_clash
    ):
        # GIVEN
        mock_parse_check_changelog_clash_args.return_value = Mock(
            files=["<file sentinel 1>"]
        )
        mock_check_changelog_clash.return_value = 1

        # WHEN
        assert check_changelog_clash.main() == 1

        # THEN
        mock_check_changelog_clash.assert_has_calls(
            [
                call(
                    "<file sentinel 1>",
                ),
            ]
        )
