# Copyright (c) 2023 Benjamin Mummery

import os
from contextlib import contextmanager
from pathlib import Path

import pytest

from _shared import resolvers


@contextmanager
def cwd(path):
    oldcwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(oldcwd)


class TestResolveFiles:
    @staticmethod
    def test_returns_empty_list_for_empty_input():
        files = resolvers._resolve_files([])

        assert files == []

    @staticmethod
    def test_returns_list_for_single_valid_file(tmp_path):
        p = tmp_path / "hello.txt"
        p.write_text("")

        with cwd(tmp_path):
            files = resolvers._resolve_files("hello.txt")

        assert files == [Path("hello.txt")]

    @staticmethod
    def test_returns_list_for_multiple_valid_files(tmp_path):
        p1 = tmp_path / "hello.txt"
        p2 = tmp_path / "goodbye.py"
        for file in [p1, p2]:
            file.write_text("")

        with cwd(tmp_path):
            files = resolvers._resolve_files(["hello.txt", "goodbye.py"])

        assert files == [Path("hello.txt"), Path("goodbye.py")]

    @staticmethod
    def test_raises_exception_for_missing_file(tmp_path):
        p1 = tmp_path / "hello.txt"
        p1.write_text("")

        with cwd(tmp_path):
            with pytest.raises(FileNotFoundError):
                resolvers._resolve_files(["hello.txt", "goodbye.py"])
