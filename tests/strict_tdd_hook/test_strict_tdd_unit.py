from strict_tdd_hook import strict_tdd


class TestConstructFileLists:
    @staticmethod
    def test_empty_list():
        assert ([], [], []) == strict_tdd._construct_file_lists([])
