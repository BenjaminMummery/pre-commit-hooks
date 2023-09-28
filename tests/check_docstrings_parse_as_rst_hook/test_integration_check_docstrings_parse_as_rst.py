# Copyright (c) 2023 Benjamin Mummery

from src.check_docstrings_parse_as_rst_hook import check_docstrings_parse_as_rst


class TestNoChanges:
    @staticmethod
    def test_no_files_changed(mocker):
        mocker.patch("sys.argv", ["stub_name"])

        assert check_docstrings_parse_as_rst.main() == 0

    @staticmethod
    def test_changed_files_have_docstrings(mocker, cwd, tmp_path):
        # GIVEN
        files = ["hello.py", ".hello.py", "_hello.py"]
        input_content = "# <file {file} content sentinel>\ndef main():\n    pass"
        for file in files:
            f = tmp_path / file
            f.write_text(input_content.format(file=file))
        mocker.patch("sys.argv", ["stub_name"] + files)

        # WHEN
        with cwd(tmp_path):
            assert check_docstrings_parse_as_rst.main() == 0

        # THEN
        for file in files:
            with open(tmp_path / file, "r") as f:
                output_content = f.read()
            assert output_content == input_content.format(file=file)

    @staticmethod
    def test_all_docstrings_are_correct_rst(mocker, cwd, tmp_path):
        # GIVEN
        files = ["hello.py", ".hello.py", "_hello.py"]
        input_content = (
            "# <file {file} content sentinel>\n"
            "def main():\n"
            '    """Valid rst."""'
            "    pass"
        )
        for file in files:
            f = tmp_path / file
            f.write_text(input_content.format(file=file))
        mocker.patch("sys.argv", ["stub_name"] + files)

        # WHEN
        with cwd(tmp_path):
            assert check_docstrings_parse_as_rst.main() == 0

        # THEN
        for file in files:
            with open(tmp_path / file, "r") as f:
                output_content = f.read()
        assert output_content == input_content.format(file=file)
