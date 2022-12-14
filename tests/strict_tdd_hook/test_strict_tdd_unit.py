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
