# Copyright (c) 2023 Benjamin Mummery

import pytest

from sort_file_contents_hook import sort_file_contents

class TestSortContents:
    @staticmethod
    @pytest.mark.parametrize("file_contents, expected_call", [
        ("A\nC\nB", ["A\n", "C\n", "B"]),
        ("A\n\nC\n", ["A\n", "\n", "C\n"]),
    ])
    def test_file_read(file_contents, expected_call, tmp_path, mocker):
        f = tmp_path / "blah.txt"
        f.write_text(file_contents)
        mock_parse_sections = mocker.patch(
            "sort_file_contents_hook.sort_file_contents._parse_sections"
        )
        
        sort_file_contents._sort_contents(f)
        
        mock_parse_sections.assert_called_once_with(expected_call)

class TestParseArgs:
    @staticmethod
    @pytest.mark.parametrize(
        "file_arg", [[], ["stub_file"], ["stub_file_1", "stub_file_2"]]
    )
    def test_argument_passing(mocker, file_arg):
        mock_file_resolver = mocker.patch(
            "_shared.resolvers._resolve_files",
            return_value="<file sentinel>",
        )
        mocker.patch("sys.argv", ["stub", *file_arg])

        args = sort_file_contents._parse_args()

        mock_file_resolver.assert_called_once_with(file_arg)
        assert args.files == "<file sentinel>"
