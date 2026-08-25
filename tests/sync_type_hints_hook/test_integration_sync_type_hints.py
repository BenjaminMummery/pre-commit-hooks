# Copyright (c) 2025-2026 Benjamin Mummery
import pytest

from pytest_git import GitRepo
from pytest_mock import MockerFixture

from conftest import add_changed_files, assert_matching
from src.sync_type_hints_hook import sync_type_hints

google_input = '''def greet(name, count):
    """Say hello.

    Args:
        name (str): Who to greet.
        count (int): How many times.

    Returns:
        bool: Whether greeting succeeded.
    """
    return True
'''

google_output = '''def greet(name: str, count: int) -> bool:
    """Say hello.

    Args:
        name (str): Who to greet.
        count (int): How many times.

    Returns:
        bool: Whether greeting succeeded.
    """
    return True
'''


@pytest.fixture()
def mock_colour(mocker):
    mocker.patch(
        "src.sync_type_hints_hook.sync_type_hints.print_diff.REMOVED_COLOUR",
        "",
    )
    mocker.patch(
        "src.sync_type_hints_hook.sync_type_hints.print_diff.ADDED_COLOUR",
        "",
    )
    mocker.patch(
        "src.sync_type_hints_hook.sync_type_hints.print_diff.END_COLOUR",
        "",
    )


class TestAddMissingAnnotations:
    @staticmethod
    def test_google_docstring(
        capsys: pytest.CaptureFixture,
        mocker: MockerFixture,
        git_repo: GitRepo,
        cwd,
        mock_colour,
    ):
        add_changed_files("hello.py", google_input, git_repo, mocker)

        with cwd(git_repo.workspace):
            assert sync_type_hints.main() == 1

        with open(git_repo.workspace / "hello.py") as handle:
            output_content = handle.read()

        assert_matching(
            "output content",
            "expected content",
            output_content,
            google_output,
        )
        captured = capsys.readouterr()
        assert "hello.py" in captured.out

    @staticmethod
    def test_adds_signature_types_to_docstring(
        mocker: MockerFixture,
        git_repo: GitRepo,
        cwd,
    ):
        source = '''def greet(name: str) -> bool:
    """Say hello.

    Args:
        name: Who to greet.

    Returns:
        Whether greeting succeeded.
    """
    return True
'''
        expected = source.replace("name: Who", "name (str): Who").replace(
            "Whether greeting",
            "bool: Whether greeting",
        )
        add_changed_files("hello.py", source, git_repo, mocker)

        with cwd(git_repo.workspace):
            assert sync_type_hints.main() == 1

        with open(git_repo.workspace / "hello.py") as handle:
            assert_matching("output", "expected", handle.read(), expected)

    @staticmethod
    def test_preserves_colon_in_untyped_yield_description(
        mocker: MockerFixture,
        git_repo: GitRepo,
        cwd,
    ):
        source = '''from collections.abc import Iterator


def mappings() -> Iterator[dict[str, str]]:
    """Build mappings.

    Yields:
        Partial maps ``{initial_label: target_label, ...}`` that localize.
    """
'''
        expected = source.replace(
            "Partial maps",
            "Iterator[dict[str, str]]: Partial maps",
        )
        add_changed_files("mappings.py", source, git_repo, mocker)

        with cwd(git_repo.workspace):
            assert sync_type_hints.main() == 1

        with open(git_repo.workspace / "mappings.py") as handle:
            assert_matching("output", "expected", handle.read(), expected)


class TestTypeClash:
    @staticmethod
    def test_raises_on_clash(
        capsys: pytest.CaptureFixture,
        mocker: MockerFixture,
        git_repo: GitRepo,
        cwd,
    ):
        source = '''def greet(name: int):
    """Say hello.

    Args:
        name (str): Who to greet.
    """
    return True
'''
        add_changed_files("hello.py", source, git_repo, mocker)

        with cwd(git_repo.workspace):
            assert sync_type_hints.main() == 1

        with open(git_repo.workspace / "hello.py") as handle:
            assert handle.read() == source

        captured = capsys.readouterr()
        assert "type clash" in captured.err


class TestPreferSignature:
    @staticmethod
    def test_updates_docstring(
        capsys: pytest.CaptureFixture,
        mocker: MockerFixture,
        git_repo: GitRepo,
        cwd,
    ):
        source = '''def greet(name: int) -> bool:
    """Say hello.

    Args:
        name (str): Who to greet.

    Returns:
        str: A message.
    """
    return True
'''
        expected = '''def greet(name: int) -> bool:
    """Say hello.

    Args:
        name (int): Who to greet.

    Returns:
        bool: A message.
    """
    return True
'''
        add_changed_files("hello.py", source, git_repo, mocker)
        mocker.patch(
            "sys.argv",
            ["stub_name", "--on-clash", "prefer-signature", "hello.py"],
        )

        with cwd(git_repo.workspace):
            assert sync_type_hints.main() == 1

        with open(git_repo.workspace / "hello.py") as handle:
            assert_matching("output", "expected", handle.read(), expected)


class TestSignatureTypesOnly:
    @staticmethod
    def test_removes_google_types(
        mocker: MockerFixture,
        git_repo: GitRepo,
        cwd,
    ):
        source = '''def greet(name: str) -> bool:
    """Say hello.

    Args:
        name (str): Who to greet.

    Returns:
        bool: Whether greeting succeeded.
    """
    return True
'''
        expected = '''def greet(name: str) -> bool:
    """Say hello.

    Args:
        name: Who to greet.

    Returns:
        Whether greeting succeeded.
    """
    return True
'''
        add_changed_files("hello.py", source, git_repo, mocker)
        mocker.patch(
            "sys.argv",
            ["stub_name", "--signature-types-only", "hello.py"],
        )

        with cwd(git_repo.workspace):
            assert sync_type_hints.main() == 1

        with open(git_repo.workspace / "hello.py") as handle:
            assert_matching("output", "expected", handle.read(), expected)

    @staticmethod
    def test_signature_types_only_moves_types_to_signature(
        mocker: MockerFixture,
        git_repo: GitRepo,
        cwd,
    ):
        source = '''def greet(name):
    """Say hello.

    Args:
        name (str): Who to greet.
    """
    return True
'''
        expected = source.replace("name):", "name: str):").replace(
            "name (str):",
            "name:",
        )
        add_changed_files("hello.py", source, git_repo, mocker)
        mocker.patch(
            "sys.argv",
            ["stub_name", "--signature-types-only", "hello.py"],
        )

        with cwd(git_repo.workspace):
            assert sync_type_hints.main() == 1

        with open(git_repo.workspace / "hello.py") as handle:
            assert_matching("output", "expected", handle.read(), expected)
