# Copyright (c) 2023 Benjamin Mummery


import pytest
from freezegun import freeze_time

from src.add_copyright_hook import add_copyright

# Source code has the form:
#
# main()
# ├── _parse_args()
# |   ├── _resolve_user_name()
# |   ├── _resolve_year()
# |   ├── _resolve_format()
# |   └── resolvers._resolve_files()
# └── _ensure_copyright_string()
#     ├── _parse_copyright_string()
#     |   └── _parse_years()
#     ├── _copyright_is_current()
#     ├── _update_copyright_string()
#     ├── _construct_copyright_string
#     |   └── [_parse_copyright_string]
#     └── _insert_copyright_string
#         └── _has_shebang()
#
# Identified integrated components:
#
# - _parse_args()
# - _ensure_copyright_string()
# - _parse_copyright_string()
# - _construct_copyright_string()
# - _insert_copyright_string

class TestParseArgs:
    @staticmethod
    def test_something(mocker):
        mocker.patch("sys.argv", return_value=["", ])

class TestEnsureCopyrightString:
    @staticmethod
    @pytest.mark.parametrize("copyright_string", ["# COPYRIGHT 2012 ABADDON THE DESPOILER"])
    def test_returns_0_for_extant_copyright_string(copyright_string, tmp_path):
        # GIVEN
        file = tmp_path / "file"
        file.write_text(copyright_string)
        
        # WHEN
        assert add_copyright._ensure_copyright_string(file, "", 2012, "") == 0
        
        # THEN
        with open(file) as f:
            contents = f.read()
        assert contents == copyright_string
    
    @staticmethod
    @pytest.mark.parametrize("contents", [
        '"""docstring"""', "def foo():\n    print('bar')\n"
    ])
    def test_adds_copyright_string_before_file_contents(contents, tmp_path):
        # GIVEN
        file = tmp_path / "file"
        file.write_text(contents)
        format = "{name} {year}"
        expected = f"<name sentinel> 1111\n\n{contents}"
        
        # WHEN
        assert add_copyright._ensure_copyright_string(file, "<name sentinel>", 1111, format) == 1
        
        # THEN
        with open(file) as f:
            c = f.read()
        assert c == expected, f"out:\n{c}\nexpected:\n{expected}"
        
    @staticmethod
    def test_adds_copyright_string_to_empty_file(tmp_path):
        # GIVEN
        file = tmp_path / "file"
        file.write_text('')
        format = "{name} {year}"
        expected = f"<name sentinel> 1111\n"
        
        # WHEN
        assert add_copyright._ensure_copyright_string(file, "<name sentinel>", 1111, format) == 1
        
        # THEN
        with open(file) as f:
            c = f.read()
        assert c == expected, f"out:\n{c}\nexpected:\n{expected}"
        
    @staticmethod
    @pytest.mark.parametrize("contents", [
        '"""docstring"""', "def foo():\n    print('bar')\n"
    ])
    def test_adds_copyright_string_after_shebang(contents, tmp_path):
        # GIVEN
        file = tmp_path / "file"
        file.write_text(f"#!/blah\n\n{contents}")
        format = "{name} {year}"
        expected = f"#!/blah\n\n<name sentinel> 1111\n\n{contents}"
        
        # WHEN
        assert add_copyright._ensure_copyright_string(file, "<name sentinel>", 1111, format) == 1
        
        # THEN
        with open(file) as f:
            c = f.read()
        assert c == expected, f"out:\n{c}\nexpected:\n{expected}"
        
    
    @staticmethod
    @pytest.mark.parametrize("contents, expected", [
        ("# COPYRIGHT 1111 ABADDON THE DESPOILER\n", "# COPYRIGHT 1111 - 2222 ABADDON THE DESPOILER\n"),
        ("# COPYRIGHT 1111-1112 ABADDON THE DESPOILER\n", "# COPYRIGHT 1111-2222 ABADDON THE DESPOILER\n"),
    ])
    def test_updates_existing_copyright_string(contents, expected, tmp_path):
        # GIVEN
        file = tmp_path / "file"
        file.write_text(contents)
        
        # WHEN
        assert add_copyright._ensure_copyright_string(file, "<name sentinel>", 2222, format) == 1
        
        # THEN
        with open(file) as f:
            c = f.read()
        assert c == expected, f"out:\n{c}\nexpected:\n{expected}"
        
    
class TestParseCopyrightString:
    @staticmethod
    def test_early_return_for_no_copyright_string():
        assert add_copyright._parse_copyright_string("") == None
    
    @staticmethod
    @pytest.mark.parametrize("input, expected", [
        ("# COPYRIGHT 2001 Stanley Kubrik", add_copyright.ParsedCopyrightString("#", "COPYRIGHT", 2001, 2001, "Stanley Kubrik", "# COPYRIGHT 2001 Stanley Kubrik")),
        ("# COPYRIGHT 2001-2023 Stanley Kubrik", add_copyright.ParsedCopyrightString("#", "COPYRIGHT", 2001, 2023, "Stanley Kubrik", "# COPYRIGHT 2001-2023 Stanley Kubrik"))
    ])
    def test_parsing(input, expected):
        out = add_copyright._parse_copyright_string(input) 
        assert out == expected, f"{out}\n{expected}"
    

class TestConstructCopyrightString:
    @staticmethod
    @pytest.mark.parametrize("format, expected", [("{name} {year}", "<name sentinel> 1111")])
    def test_formatting(format, expected):
        assert add_copyright._construct_copyright_string("<name sentinel>", 1111, format) == expected
    

    
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
    