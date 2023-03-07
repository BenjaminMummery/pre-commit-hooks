# Copyright (c) 2023 Benjamin Mummery

import pytest

from sort_gitignore_hook import sort_gitignore


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

        args = sort_gitignore._parse_args()

        mock_file_resolver.assert_called_once_with(file_arg)
        assert args.files == "<file sentinel>"
