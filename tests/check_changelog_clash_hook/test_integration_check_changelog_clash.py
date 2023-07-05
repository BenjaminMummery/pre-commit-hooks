# Copyright (c) 2023 Benjamin Mummery

import json

from src.check_changelog_clash_hook import check_changelog_clash


class TestParsingSections:
    @staticmethod
    def test_happy_path():
        input = [
            "# Top level heading",
            "foo",
            "bar",
            "## second level heading 1",
            "bux",
            "bax",
            "## second level heading 2",
            "fop",
            "fup",
            "### third level heading 1",
            "foobar",
            "## second level heading 3",
            "fuz",
            "## empty section",
            "## second level heading 4",
            "flib",
        ]
        expected_output = {
            "Top level heading": {
                "lines": ["foo", "bar"],
                "second level heading 1": {"lines": ["bux", "bax"]},
                "second level heading 2": {
                    "lines": ["fop", "fup"],
                    "third level heading 1": {"lines": ["foobar"]},
                },
                "second level heading 3": {"lines": ["fuz"]},
                "empty section": {"lines": []},
                "second level heading 4": {"lines": ["flib"]},
            }
        }

        ret = check_changelog_clash._parse_subsections(input)
        print(json.dumps(ret, indent=4))
        assert ret == expected_output

    @staticmethod
    def test_no_headings():
        # GIVEN
        input = ["1", "2", "3"]

        # WHEN
        ret = check_changelog_clash._parse_subsections(input)

        # THEN
        assert ret["lines"] == input, json.dumps(ret, indent=4)
