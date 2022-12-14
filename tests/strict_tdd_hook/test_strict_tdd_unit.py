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
