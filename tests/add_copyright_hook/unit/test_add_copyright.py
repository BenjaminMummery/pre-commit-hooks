from add_copyright_hook import add_copyright


class TestParseArgs:
    @staticmethod
    def test_no_files(mocker):
        mocker.patch("sys.argv", ["stub name"])

        args = add_copyright._parse_args()

        assert args.files == []

    @staticmethod
    def test_single_file(mocker):
        filename = "stub_file.py"
        mocker.patch("sys.argv", ["stub_name", filename])

        args = add_copyright._parse_args()

        assert args.files == [filename]

    @staticmethod
    def test_multiple_files(mocker):
        filenames = ["stub_file_1", "stub_file_2", "subdir/stub_file_3"]
        mocker.patch("sys.argv", ["stub_name"] + filenames)

        args = add_copyright._parse_args()

        assert args.files == filenames
