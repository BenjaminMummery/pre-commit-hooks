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
    mocker.patch(f"{add_copyright.__name__}.Repo", return_value=mocked_repo)
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
            side_effect=InvalidGitRepositoryError,
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
            return_value=mocked_argparse,
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
        mocker.patch(f"{add_copyright.__name__}._has_shebang", return_value=False)
        copyright = "<copyright sentinel>"
        content += "\n"

        # WHEN
        ret = add_copyright._add_copyright_string_to_content(content, copyright)

        # THEN
        assert ret == f"{copyright}\n\n{content}"

    @staticmethod
    def test_adds_trailing_newline(mocker: MockerFixture, content: str):
        # GIVEN
        mocker.patch(f"{add_copyright.__name__}._has_shebang", return_value=False)
        copyright = "<copyright sentinel>"

        # WHEN
        ret = add_copyright._add_copyright_string_to_content(content, copyright)

        # THEN
        assert ret == f"{copyright}\n\n{content}\n"

    @staticmethod
    def test_keeps_shebang_first(mocker: MockerFixture, content: str):
        # GIVEN
        mocker.patch(f"{add_copyright.__name__}._has_shebang", return_value=True)
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
        mocker.patch(f"{add_copyright.__name__}._has_shebang", return_value=False)
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
        mocked_ensure_comment = mocker.patch(
            f"{add_copyright.__name__}._ensure_comment",
            return_value="<return sentinel>",
        )

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
        mocked_ensure_comment = mocker.patch(
            f"{add_copyright.__name__}._ensure_comment",
            return_value="<return sentinel>",
        )

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


class TestEnsureValidFormat:
    @staticmethod
    @pytest.mark.parametrize("input", ["{name}{year}"])
    def test_good_format(input):
        # All we care about is that the method doesn't raise an error
        add_copyright._ensure_valid_format(input)

    @staticmethod
    @pytest.mark.parametrize("input", ["{name}"])
    def test_bad_format(input):
        with pytest.raises(KeyError):
            add_copyright._ensure_valid_format(input)


class TestEnsureCopyrightString:
    @staticmethod
    def test_explicit_raise_invalid_format(tmp_path: Path, mocker: MockerFixture, cwd):
        # GIVEN
        mocker.patch(
            f"{add_copyright.__name__}._ensure_valid_format", side_effect=KeyError
        )
        tmp_file = tmp_path / "foo"

        # WHEN / THEN
        with pytest.raises(KeyError):
            with cwd(tmp_path):
                _ = add_copyright._ensure_copyright_string(tmp_file, Mock(), Mock())

    @staticmethod
    def test_early_return_for_existing_copyright(
        tmp_path: Path, mocker: MockerFixture, cwd
    ):
        # GIVEN
        mocker.patch(f"{add_copyright.__name__}._ensure_valid_format")
        mocker.patch(
            f"{add_copyright.__name__}.get_comment_markers",
            return_value=("#", None),
        )
        mocker.patch(
            f"{add_copyright.__name__}.parse_copyright_string", return_value=True
        )
        tmp_file = tmp_path / "foo"
        tmp_file.write_text("")

        # WHEN
        with cwd(tmp_path):
            ret = add_copyright._ensure_copyright_string(tmp_file, Mock(), Mock())

        # THEN
        assert ret == 0

    @staticmethod
    def test_uses_current_year_for_no_commits(
        tmp_path: Path, mocker: MockerFixture, cwd
    ):
        # GIVEN
        mocker.patch(f"{add_copyright.__name__}._ensure_valid_format")
        mocker.patch(
            f"{add_copyright.__name__}.get_comment_markers",
            return_value=("#", None),
        )
        mocker.patch(
            f"{add_copyright.__name__}.parse_copyright_string", return_value=False
        )
        mocker.patch(
            f"{add_copyright.__name__}._get_earliest_commit_year",
            side_effect=NoCommitsError,
        )
        mocker.patch(
            f"{add_copyright.__name__}._construct_copyright_string",
            return_value="<copyright_string_sentinel>",
        )
        name = Mock()
        tmp_file = tmp_path / "foo"
        tmp_file.write_text("")

        # WHEN
        with cwd(tmp_path):
            ret = add_copyright._ensure_copyright_string(tmp_file, name, Mock())

        # THEN
        assert ret == 1


class TestMain:
    @staticmethod
    def test_explicit_raise(mocker: MockerFixture):
        # GIVEN
        mocker.patch(
            f"{add_copyright.__name__}._read_default_configuration",
            side_effect=KeyError,
        )

        # WHEN
        with pytest.raises(KeyError):
            add_copyright.main()

    @staticmethod
    def test_early_return_for_no_files(mocker: MockerFixture):
        # GIVEN
        mocker.patch(
            f"{add_copyright.__name__}._read_default_configuration",
            return_value={},
        )
        mocker.patch(f"{add_copyright.__name__}._parse_args", return_value={})
        mocker.patch(
            f"{add_copyright.__name__}._parse_args", return_value={"files": []}
        )

        # WHEN
        ret = add_copyright.main()

        # THEN
        assert ret == 0

    @staticmethod
    def test_all_files_have_copyright(mocker: MockerFixture):
        # GIVEN
        mocker.patch(
            f"{add_copyright.__name__}._read_default_configuration",
            return_value={
                "format": None,
                "name": "<name sentinel>",
                "<language key sentinel>": None,
            },
        )
        mocker.patch(
            f"{add_copyright.__name__}._parse_args",
            return_value={"files": ["<file sentinel>"]},
        )
        mocker.patch(
            f"{add_copyright.__name__}.identify.tags_from_path",
            return_value=["<identify tag sentinel>"],
        )
        mocker.patch(
            f"{add_copyright.__name__}._ensure_copyright_string", return_value=0
        )

        # WHEN
        ret = add_copyright.main()

        # THEN
        assert ret == 0

    @staticmethod
    def test_extracting_language_specific_config(mocker: MockerFixture):
        # GIVEN
        mocker.patch(
            f"{add_copyright.__name__}._read_default_configuration",
            return_value={
                "format": None,
                "name": "<name sentinel>",
                "<language key sentinel>": {"key_sentinel": "<value sentinel>"},
            },
        )
        mocker.patch(
            f"{add_copyright.__name__}._parse_args",
            return_value={"files": ["<file sentinel>"]},
        )
        mocker.patch(
            f"{add_copyright.__name__}.identify.tags_from_path",
            return_value=["<identify tag sentinel>"],
        )
        mocker.patch(
            f"{add_copyright.__name__}.LANGUAGE_TAGS_TOMLKEYS",
            {"<identify tag sentinel>": "<language key sentinel>"},
        )
        mock_copyright_string = mocker.patch(
            f"{add_copyright.__name__}._ensure_copyright_string", return_value=0
        )

        # WHEN
        _ = add_copyright.main()

        # THEN
        mock_copyright_string.assert_called_once_with(
            Path("<file sentinel>"),
            name="<name sentinel>",
            format="Copyright (c) {year} {name}",
            key_sentinel="<value sentinel>",
        )

    @staticmethod
    @pytest.mark.parametrize("exception", [KeyError, ValueError])
    def test_explicit_reraise(mocker: MockerFixture, exception: Exception):
        # GIVEN
        mocker.patch(
            f"{add_copyright.__name__}._read_default_configuration",
            return_value={
                "format": None,
                "name": "<name sentinel>",
                "<language key sentinel>": None,
            },
        )
        mocker.patch(
            f"{add_copyright.__name__}._parse_args",
            return_value={"files": ["<file sentinel>"]},
        )
        mocker.patch(
            f"{add_copyright.__name__}.identify.tags_from_path",
            return_value=["<identify tag sentinel>"],
        )
        mocker.patch(
            f"{add_copyright.__name__}._ensure_copyright_string",
            side_effect=exception,
        )

        # WHEN / THEN
        with pytest.raises(exception):
            _ = add_copyright.main()
