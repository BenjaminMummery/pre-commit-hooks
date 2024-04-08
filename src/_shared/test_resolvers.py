# Copyright (c) 2023 - 2024 Benjamin Mummery

from pathlib import Path

import pytest

from . import resolvers


class TestResolveFiles:
    @staticmethod
    def test_returns_empty_list_for_empty_input():
        files = resolvers.resolve_files([])

        assert files == []

    @staticmethod
    def test_returns_list_for_single_valid_file(tmp_path, cwd):
        p = tmp_path / "hello.txt"
        p.write_text("")

        with cwd(tmp_path):
            files = resolvers.resolve_files("hello.txt")

        assert files == [Path("hello.txt")]

    @staticmethod
    def test_returns_list_for_multiple_valid_files(tmp_path, cwd):
        p1 = tmp_path / "hello.txt"
        p2 = tmp_path / "goodbye.py"
        for file in [p1, p2]:
            file.write_text("")

        with cwd(tmp_path):
            files = resolvers.resolve_files(["hello.txt", "goodbye.py"])

        assert files == [Path("hello.txt"), Path("goodbye.py")]

    @staticmethod
    def test_raises_exception_for_missing_file(tmp_path, cwd):
        p1 = tmp_path / "hello.txt"
        p1.write_text("")

        with cwd(tmp_path):
            with pytest.raises(FileNotFoundError):
                resolvers.resolve_files(["hello.txt", "goodbye.py"])
