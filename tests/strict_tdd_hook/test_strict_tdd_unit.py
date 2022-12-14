import pytest

from strict_tdd_hook import strict_tdd


class TestConstructFileLists:
    @staticmethod
    def test_empty_list():
        assert ([], [], []) == strict_tdd._construct_file_lists([])

    @staticmethod
    def test_src_files_only():
        filenames = ["src/foo", "src/bar"]
        assert (filenames, [], []) == strict_tdd._construct_file_lists(filenames)

    @staticmethod
    def test_test_files_only():
        filenames = ["test/foo", "test/bar"]
        assert ([], filenames, []) == strict_tdd._construct_file_lists(filenames)

    @staticmethod
    def test_etc_files_only():
        filenames = ["blah/foo", "bar"]
        assert ([], [], filenames) == strict_tdd._construct_file_lists(filenames)

    @staticmethod
    @pytest.mark.parametrize(
        "filenames, src_list, test_list, etc_list",
        [(["src/foo", "test/bar"], ["src/foo"], ["test/bar"], [])],
    )
    def test_mixed_files(filenames, src_list, test_list, etc_list):
        assert (src_list, test_list, etc_list) == strict_tdd._construct_file_lists(
            filenames
        )
