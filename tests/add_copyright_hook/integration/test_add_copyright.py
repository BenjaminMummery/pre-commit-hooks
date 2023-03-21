# Copyright (c) 2023 Benjamin Mummery


import pytest
from freezegun import freeze_time

from src.add_copyright_hook import add_copyright


class TestNoFilesToCheck:
    @staticmethod
    def test_return_0_for_no_changed_files(mocker):
        # Given
        mocker.patch("sys.argv", ["stub_name"])

        # Then
        assert add_copyright.main() == 0

    @staticmethod
    @freeze_time("1001-01-01")
    def test_return_0_if_all_files_have_copyright(mocker, git_repo, cwd):
        # Given
        p1 = git_repo.workspace / "file_1.py"
        p2 = git_repo.workspace / "file_2.txt"
        p3 = git_repo.workspace / "file_3.py"
        p4 = git_repo.workspace / "file_4.txt"

        p1.write_text("# Copyright 1001 James T. Kirk")
        p2.write_text("#COPYRIGHT 1001 KHAN")
        p3.write_text("# copyright (c) 1000 - 1001 Bones")
        p4.write_text("# Copyright 1000-1001 McCoy")
        mocker.patch(
            "sys.argv",
            ["stub_name", "file_1.py", "file_2.txt", "file_3.py", "file_4.txt"],
        )

        # Then
        with cwd(git_repo.workspace):
            assert add_copyright.main() == 0


class TestInferredNameDate:
    @staticmethod
    @freeze_time("1001-01-01")
    def test_default_formatting(mocker, git_repo, cwd):
        # Given
        username = "<username sentinel>"
        expected_content = "# Copyright (c) 1001 <username sentinel>\n"
        git_repo.run(f"git config user.name '{username}'")
        p1 = git_repo.workspace / "file_1.py"
        p2 = git_repo.workspace / "file_2.txt"
        files = [p1, p2]
        for file in files:
            file.write_text("")
        mocker.patch("sys.argv", ["stub_name", "file_1.py", "file_2.txt"])

        # When
        with cwd(git_repo.workspace):
            assert add_copyright.main() == 1

        # Then
        for file in files:
            with open(file, "r") as f:
                content: str = f.read()

            assert content == expected_content

    @staticmethod
    @freeze_time("1001-01-01")
    def test_keep_shebang_first(mocker, git_repo, capsys, cwd):
        # Given
        input_content = "#!<shebang sentinel>\n" "<content sentinel>"
        expected_content = (
            "#!<shebang sentinel>\n"
            "\n"
            "# Copyright (c) 1001 <username sentinel>\n"
            "\n"
            "<content sentinel>"
        )

        username = "<username sentinel>"
        git_repo.run(f"git config user.name '{username}'")
        p1 = git_repo.workspace / "file_1.py"
        p1.write_text(input_content)
        mocker.patch("sys.argv", ["stub_name", "file_1.py"])

        # When
        with cwd(git_repo.workspace):
            assert add_copyright.main() == 1

        # Then
        with open(p1) as f:
            out: str = f.read()
        assert out == expected_content


class TestCLINameDate:
    @staticmethod
    def test_custom_name_and_year(mocker, git_repo, cwd):
        # Given
        username = "<username sentinel>"
        date = "0000"
        p1 = git_repo.workspace / "file_1.py"
        p2 = git_repo.workspace / "file_2.txt"
        files = [p1, p2]
        for file in files:
            file.write_text("")
        mocker.patch(
            "sys.argv",
            ["stub_name", "file_1.py", "file_2.txt", "-n", username, "-y", date],
        )

        # When
        with cwd(git_repo.workspace):
            assert add_copyright.main() == 1

        # Then
        for file in files:
            with open(file, "r") as f:
                content: str = f.read()
            assert content.startswith("# Copyright (c) 0000 <username sentinel>")


class TestUpdatesExistingDateRanges:
    @staticmethod
    @freeze_time("1234-01-01")
    @pytest.mark.parametrize(
        "existing_copyright_string, expected_copyright_string",
        [
            ("# Copyright 1002 James T. Kirk", "# Copyright 1002-1234 James T. Kirk"),
            ("#COPYRIGHT 1098-1156 KHAN", "#COPYRIGHT 1098-1234 KHAN"),
        ],
    )
    @pytest.mark.xfail
    def test_updates_date_ranges(
        mocker, git_repo, existing_copyright_string, expected_copyright_string, cwd
    ):
        # Given
        p1 = git_repo.workspace / "file_1.py"
        p1.write_text(existing_copyright_string)

        mocker.patch("sys.argv", ["stub_name", "file_1.py"])

        # When
        with cwd(git_repo.workspace):
            assert add_copyright.main() == 1

        # Then
        with open(p1, "r") as f:
            content: str = f.read()
        assert content.startswith(expected_copyright_string)


class TestDefaultConfigFile:
    @staticmethod
    def test_default_config_file_location(mocker, git_repo, cwd):
        # Given
        p1 = git_repo.workspace / "file_1.py"
        p2 = git_repo.workspace / "file_2.txt"
        files = [p1, p2]
        for file in files:
            file.write_text("")
        c = git_repo.workspace / ".add-copyright-hook-config.yaml"
        c.write_text(
            "name: <name sentinel>\n"
            "year: '0000'\nformat: '# Belongs to {name} as of {year}.'"
        )
        mocker.patch("sys.argv", ["stub_name", "file_1.py", "file_2.txt"])

        # When
        with cwd(git_repo.workspace):
            assert add_copyright.main() == 1

        # Then
        for file in files:
            with open(file, "r") as f:
                content: str = f.read()
            assert content.startswith(
                "# Belongs to <name sentinel> as of 0000."
            ), content


class TestCustomConfigFile:
    @staticmethod
    @pytest.mark.parametrize(
        "filename, file_contents",
        [
            (
                "stub_filename.json",
                (
                    "{\n"
                    '    "name": "<name sentinel>",\n'
                    '    "year": "0000",\n'
                    '    "format": "# <format sentinel> {name} {year}"\n'
                    "}\n"
                ),
            ),
            (
                "stub_filename.yaml",
                (
                    "name: <name sentinel>\n"
                    "year: '0000'\n"
                    "format: '# <format sentinel> {name} {year}'\n"
                ),
            ),
        ],
    )
    def test_custom_config_file_location(
        mocker, git_repo, filename, file_contents, cwd
    ):
        # Given
        p1 = git_repo.workspace / "file_1.py"
        p2 = git_repo.workspace / "file_2.txt"
        files = [p1, p2]
        for file in files:
            file.write_text("")
        c = git_repo.workspace / filename
        c.write_text(file_contents)
        mocker.patch(
            "sys.argv", ["stub_name", "file_1.py", "file_2.txt", "-c", filename]
        )

        # When
        with cwd(git_repo.workspace):
            assert add_copyright.main() == 1

        # Then
        for file in files:
            with open(file, "r") as f:
                content: str = f.read()
            assert content.startswith(
                "# <format sentinel> <name sentinel> 0000"
            ), content
