# Copyright (c) 2023 Benjamin Mummery

import os
from contextlib import contextmanager

from freezegun import freeze_time

from add_copyright_hook import add_copyright


@contextmanager
def cwd(path):
    oldcwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(oldcwd)


def test_return_0_for_no_changed_files(mocker):
    mocker.patch("sys.argv", ["stub_name"])
    assert add_copyright.main() == 0


def test_return_0_if_all_files_have_copyright(mocker, git_repo):
    p1 = git_repo.workspace / "file_1.py"
    p2 = git_repo.workspace / "file_2.txt"
    p1.write_text("# Copyright 1701 James T. Kirk")
    p2.write_text("#COPYRIGHT 2087 KHAN")
    mocker.patch("sys.argv", ["stub_name", "file_1.py", "file_2.txt"])

    with cwd(git_repo.workspace):
        assert add_copyright.main() == 0


@freeze_time("1001-01-01")
def test_default_formatting(mocker, git_repo):
    username = "<username sentinel>"
    expected_content = "# Copyright (c) 1001 <username sentinel>\n"
    git_repo.run(f"git config user.name '{username}'")
    p1 = git_repo.workspace / "file_1.py"
    p2 = git_repo.workspace / "file_2.txt"
    files = [p1, p2]
    for file in files:
        file.write_text("")
    mocker.patch("sys.argv", ["stub_name", "file_1.py", "file_2.txt"])

    with cwd(git_repo.workspace):
        assert add_copyright.main() == 1

    for file in files:
        with open(file, "r") as f:
            content: str = f.read()

        assert content == expected_content


@freeze_time("1001-01-01")
def test_keep_shebang_first(mocker, git_repo, capsys):
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

    with cwd(git_repo.workspace):
        assert add_copyright.main() == 1

    with open(p1) as f:
        out: str = f.read()

    assert out == expected_content


def test_custom_name_and_year(mocker, git_repo):
    username = "<username sentinel>"
    date = "0000"
    p1 = git_repo.workspace / "file_1.py"
    p2 = git_repo.workspace / "file_2.txt"
    files = [p1, p2]
    for file in files:
        file.write_text("")
    mocker.patch(
        "sys.argv", ["stub_name", "file_1.py", "file_2.txt", "-n", username, "-y", date]
    )

    with cwd(git_repo.workspace):
        assert add_copyright.main() == 1

    for file in files:
        with open(file, "r") as f:
            content: str = f.read()
        assert content.startswith("# Copyright (c) 0000 <username sentinel>")
