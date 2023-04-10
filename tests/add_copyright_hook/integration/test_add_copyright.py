# Copyright (c) 2023 Benjamin Mummery


import pytest
from freezegun import freeze_time

from src.add_copyright_hook import add_copyright

# Source code has the form:
#
# main()
# ├── _parse_args()
# └── _ensure_copyright_string()
#     ├── _parse_copyright_string()
#     |   └── _parse_years()
#     ├── _copyright_is_current()
#     ├── _update_copyright_string()
#     ├── _construct_copyright_string()
#     |   └── [_parse_copyright_string]
#     └── _insert_copyright_string
#         └── _has_shebang()
#
# Identified integrated components:
#
# - _ensure_copyright_string()
# - _parse_copyright_string()
# - _construct_copyright_string()
# - _insert_copyright_string

class TestEnsureCopyrightString:
    @staticmethod
    def test_early_return_for_extant_copyright_string():
        pass
    
    @staticmethod
    def test_adds_copyright_string():
        pass
    
    @staticmethod
    def test_updates_existing_copyright_string():
        pass
    
class TestParseCopyrightString:
    @staticmethod
    def test_early_return_for_no_copyright_string():
        pass
    
    @staticmethod
    def test_parsing():
        pass
    
class TestConstructCopyrightString:
    @staticmethod
    def test_formatting():
        pass
    
    @staticmethod
    def test_checks_parsing_if_default_format_used():
        pass
    
class TestInsertCopyrightString:
    @staticmethod
    @pytest.mark.parametrize("content, expected", [
        ("Single line", "<copyright sentinel>\n\nSingle line"),
        ("Multiple\nlines", "<copyright sentinel>\n\nMultiple\nlines"),
        ("\nBlank first line", "<copyright sentinel>\n\nBlank first line")
    ])
    def test_happy_path(content, expected):
        out = add_copyright._insert_copyright_string("<copyright sentinel>", content)
        assert out == expected, f"out:\n{out}\nexpected:\n{expected}"
    
    @staticmethod
    @pytest.mark.parametrize("content, expected", [
        ("#!shebang only", "#!shebang only\n\n<copyright sentinel>"),
        ("#!shebang and\nsingle line", "#!shebang and\n\n<copyright sentinel>\n\nsingle line"),
    ])
    def test_keeps_shebang_at_top(content, expected):
        out = add_copyright._insert_copyright_string("<copyright sentinel>", content)
        assert out == expected, f"out:\n{out}\nexpected:\n{expected}"
    