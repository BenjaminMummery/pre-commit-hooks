import os
from contextlib import contextmanager

import pytest

from strict_tdd_hook import strict_tdd


class TestConstructFileLists:
    @staticmethod
    @pytest.mark.parametrize(
        "filenames, src_list, test_list, etc_list",
        [
            ([], [], [], []),
            (["src/foo", "src/bar"], ["src/foo", "src/bar"], [], []),
            (["test/foo", "test/bar"], [], ["test/foo", "test/bar"], []),
            (["blah/foo", "bar"], [], [], ["blah/foo", "bar"]),
            (["src/foo", "test/bar"], ["src/foo"], ["test/bar"], []),
        ],
    )
    def test_mixed_files(filenames, src_list, test_list, etc_list):
        assert (src_list, test_list, etc_list) == strict_tdd._parse_file_list(filenames)


@contextmanager
def cwd(path):
    oldcwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(oldcwd)


@pytest.fixture()
def tmp_testable_dir(tmp_path):
    with cwd(tmp_path):
        os.mkdir("src")
        os.mkdir("test")
    return tmp_path


class TestGetCurrentNTests:
    @staticmethod
    def test_returns_0_for_no_test_files(tmp_testable_dir):
        with cwd(tmp_testable_dir):
            assert strict_tdd._get_current_n_tests() == 0
