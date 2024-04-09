# Copyright (c) 2024 Benjamin Mummery

from unittest.mock import Mock, create_autospec

import pytest
from git.repo.base import BlameEntry
from pytest_mock import MockerFixture

from src.add_copyright_hook import add_copyright
from src.add_copyright_hook.add_copyright import (
    GitCommandError,
    InvalidGitRepositoryError,
    NoCommitsError,
    Path,
    Repo,
    argparse,
)


@pytest.fixture()
def mock_repo(mocker: MockerFixture) -> add_copyright.Repo:
    mocked_repo = create_autospec(Repo)
    mocker.patch(f"{add_copyright.__name__}.Repo", Mock(return_value=mocked_repo))
    return mocked_repo


class TestGetEarliestCommitYear:
    @staticmethod
    def test_raises_InvalidGitRepositoryError_for_nonexistent_git_repo(
        tmp_path: Path,
        cwd,
        mocker,
    ):
        # GIVEN
        mocker.patch(
            f"{add_copyright.__name__}.Repo",
            Mock(side_effect=InvalidGitRepositoryError),
        )

        # WHEN / THEN
        with pytest.raises(InvalidGitRepositoryError):
            with cwd(tmp_path):
                add_copyright._get_earliest_commit_year(Mock())

    @staticmethod
    def test_raises_NoCommitsError_for_nonexistent_git_repo(
        tmp_path: Path,
        cwd,
        mock_repo,
    ):
        # GIVEN
        mock_repo.blame.side_effect = GitCommandError(["<command sentinel>"])

        # WHEN / THEN
        with pytest.raises(NoCommitsError):
            with cwd(tmp_path):
                add_copyright._get_earliest_commit_year(Mock())

    @staticmethod
    def test_single_commit(tmp_path: Path, cwd, mock_repo):
        # GIVEN
        mock_blameentry = create_autospec(BlameEntry)
        mock_repo.blame.return_value = [mock_blameentry]

        # WHEN
        with cwd(tmp_path):
            ret = add_copyright._get_earliest_commit_year(Mock())

        # THEN
        assert ret == 1970


class TestParseArgs:
    @staticmethod
    def test_parse_args(mocker: MockerFixture):
        # GIVEN
        mocked_argparse = create_autospec(argparse.ArgumentParser)
        mocker.patch(
            f"{add_copyright.__name__}.argparse.ArgumentParser",
            Mock(return_value=mocked_argparse),
        )
        mocker.patch(
            f"{add_copyright.__name__}.resolvers.resolve_files",
            return_value=["<file sentinel>"],
        )

        # WHEN
        ret = add_copyright._parse_args()

        # THEN
        assert ret["files"] == ["<file sentinel>"]


class TestGetGitUserName:
    @staticmethod
    @pytest.mark.parametrize("return_name", [None, ""])
    def test_raises_valueerror_for_no_configured_username(mock_repo, return_name):
        # GIVEN
        mock_reader = Mock()
        mock_reader.get_value.return_value = return_name
        mock_repo.config_reader.return_value = mock_reader

        # WHEN
        with pytest.raises(ValueError) as e:
            _ = add_copyright._get_git_user_name()

        # THEN
        assert e.exconly() == "ValueError: The git username is not configured."

    @staticmethod
    def test_get_git_user_name(mock_repo):
        # GIVEN
        mock_reader = Mock()
        mock_reader.get_value.return_value = "<name sentinel>"
        mock_repo.config_reader.return_value = mock_reader

        # WHEN
        ret = add_copyright._get_git_user_name()

        # THEN
        assert ret == "<name sentinel>"


class TestHasShebang:
    @staticmethod
    @pytest.mark.parametrize("input", ["#! thing/other"])
    def test_returns_true_for_shebang(input):
        assert add_copyright._has_shebang(input)

    @staticmethod
    @pytest.mark.parametrize("input", ["# Not a shebang"])
    def test_returns_false_for_no_shebang(input):
        assert not add_copyright._has_shebang(input)


@pytest.mark.parametrize(
    "content", ["<content sentinel>", "<multi\nline\ncontent\nsentinel>"]
)
class TestAddCopyrightStringToContent:
    @staticmethod
    def test_simple_content_block(mocker: MockerFixture, content: str):
        # GIVEN
        mocker.patch(f"{add_copyright.__name__}._has_shebang", Mock(return_value=False))
        copyright = "<copyright sentinel>"
        content += "\n"

        # WHEN
        ret = add_copyright._add_copyright_string_to_content(content, copyright)

        # THEN
        assert ret == f"{copyright}\n\n{content}"

    @staticmethod
    def test_adds_trailing_newline(mocker: MockerFixture, content: str):
        # GIVEN
        mocker.patch(f"{add_copyright.__name__}._has_shebang", Mock(return_value=False))
        copyright = "<copyright sentinel>"

        # WHEN
        ret = add_copyright._add_copyright_string_to_content(content, copyright)

        # THEN
        assert ret == f"{copyright}\n\n{content}\n"

    @staticmethod
    def test_keeps_shebang_first(mocker: MockerFixture, content: str):
        # GIVEN
        mocker.patch(f"{add_copyright.__name__}._has_shebang", Mock(return_value=True))
        copyright = "<copyright sentinel>"
        shebang = "<shebang sentinel>"

        # WHEN
        ret = add_copyright._add_copyright_string_to_content(
            shebang + "\n" + content, copyright
        )

        # THEN
        assert ret == f"{shebang}\n\n{copyright}\n\n{content}\n"

    @staticmethod
    def test_handles_leading_newlines(mocker: MockerFixture, content: str):
        # GIVEN
        mocker.patch(f"{add_copyright.__name__}._has_shebang", Mock(return_value=False))
        copyright = "<copyright sentinel>"

        # WHEN
        ret = add_copyright._add_copyright_string_to_content("\n" + content, copyright)

        # THEN
        assert ret == f"{copyright}\n\n{content}\n"


@pytest.mark.parametrize("name", ["<name sentinel>"])
class TestConstructCopyrightString:
    @staticmethod
    def test_single_year(name: str, mocker: MockerFixture):
        # GIVEN
        start_year = 2000
        end_year = start_year
        format = "year: {year}, name: {name}"
        comment_markers = Mock()
        mocked_ensure_comment = Mock(return_value="<return sentinel>")
        mocker.patch(f"{add_copyright.__name__}._ensure_comment", mocked_ensure_comment)

        # WHEN
        ret = add_copyright._construct_copyright_string(
            name, start_year, end_year, format, comment_markers
        )

        # THEN
        assert ret == "<return sentinel>"
        mocked_ensure_comment.assert_called_once_with(
            f"year: {start_year}, name: {name}", comment_markers
        )

    @staticmethod
    def test_year_range(name: str, mocker: MockerFixture):
        # GIVEN
        start_year = 2000
        end_year = 3000
        format = "year: {year}, name: {name}"
        comment_markers = Mock()
        mocked_ensure_comment = Mock(return_value="<return sentinel>")
        mocker.patch(f"{add_copyright.__name__}._ensure_comment", mocked_ensure_comment)

        # WHEN
        ret = add_copyright._construct_copyright_string(
            name, start_year, end_year, format, comment_markers
        )

        # THEN
        assert ret == "<return sentinel>"
        mocked_ensure_comment.assert_called_once_with(
            f"year: {start_year} - {end_year}, name: {name}", comment_markers
        )


class TestEnsureComment:
    class TestSingleLine:
        @staticmethod
        def test_adds_leading_comment_marker():
            # GIVEN
            string = "<input sentinel>"
            comment_markers = ("#", None)

            # WHEN
            ret = add_copyright._ensure_comment(string, comment_markers)

            # THEN
            assert ret == "# <input sentinel>"

        @staticmethod
        def test_adds_enclosing_comment_markers():
            # GIVEN
            string = "<input sentinel>"
            comment_markers = ("#", "!")

            # WHEN
            ret = add_copyright._ensure_comment(string, comment_markers)

            # THEN
            assert ret == "# <input sentinel> !"

    class TestMultipleLines:
        @staticmethod
        def test_adds_leading_comment_marker():
            # GIVEN
            string = "<input line 1 sentinel>\n<input line 2 sentinel>"
            comment_markers = ("#", None)

            # WHEN
            ret = add_copyright._ensure_comment(string, comment_markers)

            # THEN
            assert ret == "# <input line 1 sentinel>\n# <input line 2 sentinel>"

        @staticmethod
        def test_adds_enclosing_comment_markers():
            # GIVEN
            string = "<input line 1 sentinel>\n<input line 2 sentinel>"
            comment_markers = ("#", "!")

            # WHEN
            ret = add_copyright._ensure_comment(string, comment_markers)

            # THEN
            assert ret == "# <input line 1 sentinel> !\n# <input line 2 sentinel> !"

    class TestReadDefaultConfiguration:
        @staticmethod
        def test_no_config_file(cwd, tmp_path: Path, mocker: MockerFixture):
            # GIVEN
            mocker.patch(
                f"{add_copyright.__name__}.LANGUAGE_TAGS_TOMLKEYS",
                {"mock_key": "mock_value"},
            )

            # WHEN
            with cwd(tmp_path):
                ret = add_copyright._read_default_configuration()

            # THEN
            assert ret == {"name": None, "format": None, "mock_value": None}

        @staticmethod
        def test_pyproject_toml_config(cwd, tmp_path: Path, mocker: MockerFixture):
            # GIVEN
            mocker.patch(
                f"{add_copyright.__name__}.LANGUAGE_TAGS_TOMLKEYS",
                {"mock_key": "mock_value"},
            )
            config_file = tmp_path / "pyproject.toml"
            config_file.write_text('[tool.add_copyright]\nname = "my name"')

            # WHEN
            with cwd(tmp_path):
                ret = add_copyright._read_default_configuration()

            # THEN
            assert ret == {"name": "my name", "format": None, "mock_value": None}

        @staticmethod
        def test_raises_KeyError_for_unsupported_keys(
            cwd, tmp_path: Path, mocker: MockerFixture
        ):
            # GIVEN
            mocker.patch(
                f"{add_copyright.__name__}.LANGUAGE_TAGS_TOMLKEYS",
                {"mock_key": "mock_value"},
            )
            config_file = tmp_path / "pyproject.toml"
            config_file.write_text(
                '[tool.add_copyright]\nname = "my name"\nflugendorf = "something"'
            )

            # WHEN
            with pytest.raises(KeyError) as e:
                with cwd(tmp_path):
                    _ = add_copyright._read_default_configuration()

            # THEN
            assert "flugendorf" in e.exconly()

        @staticmethod
        def test_language_specific_subkeys(cwd, tmp_path: Path, mocker: MockerFixture):
            # GIVEN
            mocker.patch(
                f"{add_copyright.__name__}.LANGUAGE_TAGS_TOMLKEYS",
                {"mock_key": "mock_value"},
            )
            config_file = tmp_path / "pyproject.toml"
            config_file.write_text(
                '[tool.add_copyright.mock_value]\nformat="<format sentinel>"'
            )

            # WHEN
            with cwd(tmp_path):
                ret = add_copyright._read_default_configuration()

            # THEN
            assert ret == {
                "name": None,
                "format": None,
                "mock_value": {"format": "<format sentinel>"},
            }

        @staticmethod
        def test_raises_KeyError_for_unsupported_language_specific_subkey(
            cwd, tmp_path: Path, mocker: MockerFixture
        ):
            # GIVEN
            mocker.patch(
                f"{add_copyright.__name__}.LANGUAGE_TAGS_TOMLKEYS",
                {"mock_key": "mock_value"},
            )
            config_file = tmp_path / "pyproject.toml"
            config_file.write_text(
                '[tool.add_copyright.mock_value]\nformat="<format sentinel>"\nbadkey="something"'  # NOQA: E501
            )

            # WHEN
            with pytest.raises(KeyError) as e:
                with cwd(tmp_path):
                    _ = add_copyright._read_default_configuration()

            # THEN
            assert "badkey" in e.exconly()
