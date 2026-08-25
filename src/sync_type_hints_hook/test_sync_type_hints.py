# Copyright (c) 2025-2026 Benjamin Mummery

import ast
import textwrap

import pytest

from src.sync_type_hints_hook.docstring_types import (
    parse_docstring_types,
    rewrite_docstring_types,
    types_match,
)
from src.sync_type_hints_hook.exceptions import TypeClashError
from src.sync_type_hints_hook.signature_types import (
    annotation_to_str,
    build_signature_edits,
    parse_signature_types,
)
from src.sync_type_hints_hook.source_edits import apply_edits
from src.sync_type_hints_hook.sync_type_hints import (
    HookConfig,
    _collect_functions,
    _get_docstring_node,
    _load_config,
    _plan_function_edits,
    _sync_type_hints,
)


class TestParseGoogleDocstrings:
    @staticmethod
    def test_extracts_args_and_returns():
        docstring = (
            "Do something.\n\n"
            "Args:\n"
            "    name (str): The name.\n"
            "    count (int, optional): The count.\n\n"
            "Returns:\n"
            "    bool: Whether it worked.\n"
        )
        info = parse_docstring_types(docstring)
        assert info.style == "google"
        assert info.args == {"name": "str", "count": "int"}
        assert info.returns == "bool"

    @staticmethod
    def test_detects_untyped_entries():
        info = parse_docstring_types(
            "Args:\n    name: The name.\n\nReturns:\n    Whether it worked.\n",
        )
        assert info.style == "google"
        assert info.documented_args == {"name"}
        assert info.args == {}
        assert info.documents_return is True
        assert info.returns is None

    @staticmethod
    def test_colon_in_untyped_yield_description_is_not_a_type_separator():
        info = parse_docstring_types(
            "Yields:\n"
            "    Partial maps ``{initial_label: target_label, ...}`` that localize.\n",
        )
        assert info.style == "google"
        assert info.documents_return is True
        assert info.returns is None


class TestParseNumpyDocstrings:
    @staticmethod
    def test_extracts_args_and_returns():
        docstring = (
            "Do something.\n\n"
            "Parameters\n"
            "----------\n"
            "name : str\n"
            "    The name.\n"
            "count : int\n"
            "    The count.\n\n"
            "Returns\n"
            "-------\n"
            "bool\n"
            "    Whether it worked.\n"
        )
        info = parse_docstring_types(docstring)
        assert info.style == "numpy"
        assert info.args == {"name": "str", "count": "int"}
        assert info.returns == "bool"

    @staticmethod
    def test_detects_untyped_entries():
        info = parse_docstring_types(
            "Parameters\n----------\nname\n    The name.\n\n"
            "Returns\n-------\n    Whether it worked.\n",
        )
        assert info.style == "numpy"
        assert info.documented_args == {"name"}
        assert info.args == {}
        assert info.documents_return is True
        assert info.returns is None

    @staticmethod
    def test_extracts_return_aligned_with_indented_section():
        info = parse_docstring_types(
            "Summary.\n\n"
            "    Returns\n"
            "    -------\n"
            "    ActiveSpaceSelectionResult\n"
            "        Uniform descriptive result.\n",
        )
        assert info.style == "numpy"
        assert info.documents_return is True
        assert info.returns == "ActiveSpaceSelectionResult"


class TestParseSphinxDocstrings:
    @staticmethod
    def test_extracts_args_and_returns():
        docstring = (
            "Do something.\n\n"
            ":param str name: The name.\n"
            ":param int count: The count.\n"
            ":rtype: bool\n"
        )
        info = parse_docstring_types(docstring)
        assert info.style == "sphinx"
        assert info.args == {"name": "str", "count": "int"}
        assert info.returns == "bool"

    @staticmethod
    def test_detects_untyped_entries():
        info = parse_docstring_types(
            ":param name: The name.\n:return: Whether it worked.\n",
        )
        assert info.style == "sphinx"
        assert info.documented_args == {"name"}
        assert info.args == {}
        assert info.documents_return is True
        assert info.returns is None

    @staticmethod
    def test_supports_type_directives():
        docstring = ":type name: str\n:type count: int\n:rtype: bool\n"
        info = parse_docstring_types(docstring)
        assert info.style == "sphinx"
        assert info.args == {"name": "str", "count": "int"}
        assert info.returns == "bool"


class TestTypesMatch:
    @staticmethod
    @pytest.mark.parametrize(
        ("left", "right", "expected"),
        [
            ("str", "str", True),
            ("int", "str", False),
            ("Optional[str]", "Optional[str]", True),
            ("int, optional", "int", True),
        ],
    )
    def test_normalizes_types(left, right, expected):
        assert types_match(left, right) is expected


class TestRewriteDocstrings:
    @staticmethod
    @pytest.mark.parametrize(
        ("docstring", "expected_arg", "expected_return"),
        [
            (
                "Args:\n    name: The name.\n\nReturns:\n    Whether it worked.",
                "name (str): The name.",
                "bool: Whether it worked.",
            ),
            (
                "Parameters\n----------\nname\n    The name.\n\n"
                "Returns\n-------\n    Whether it worked.",
                "name : str",
                "bool\n    Whether it worked.",
            ),
            (
                ":param name: The name.\n:return: Whether it worked.",
                ":param str name: The name.",
                ":rtype: bool",
            ),
        ],
    )
    def test_add_types_to_untyped_entries(docstring, expected_arg, expected_return):
        info = parse_docstring_types(docstring)
        rewritten, changed = rewrite_docstring_types(
            docstring,
            info,
            remove_types=False,
            updated_args={"name": "str"},
            updated_return="bool",
        )
        assert changed is True
        assert expected_arg in rewritten
        assert expected_return in rewritten

    @staticmethod
    def test_remove_google_types():
        docstring = (
            "Summary.\n\n"
            "Args:\n"
            "    name (str): The name.\n\n"
            "Returns:\n"
            "    bool: Whether it worked.\n"
        )
        info = parse_docstring_types(docstring)
        rewritten, changed = rewrite_docstring_types(
            docstring,
            info,
            remove_types=True,
        )
        assert changed is True
        assert "(str)" not in rewritten
        assert "name: The name." in rewritten
        assert "Whether it worked." in rewritten

    @staticmethod
    def test_update_google_types():
        docstring = "Args:\n    name (str): The name.\n"
        info = parse_docstring_types(docstring)
        rewritten, changed = rewrite_docstring_types(
            docstring,
            info,
            remove_types=False,
            updated_args={"name": "int"},
        )
        assert changed is True
        assert "name (int): The name." in rewritten

    @staticmethod
    def test_add_google_yield_type_before_description_containing_colon():
        docstring = (
            "Yields:\n"
            "    Partial wire-label maps ``{initial_label: target_label, ...}`` that\n"
            "    localize every target.\n"
        )
        info = parse_docstring_types(docstring)
        rewritten, changed = rewrite_docstring_types(
            docstring,
            info,
            remove_types=False,
            updated_return="Iterator[WireLabelRoutingMap]",
        )
        assert changed is True
        assert rewritten == (
            "Yields:\n"
            "    Iterator[WireLabelRoutingMap]: Partial wire-label maps "
            "``{initial_label: target_label, ...}`` that\n"
            "    localize every target."
        )

    @staticmethod
    def test_add_numpy_return_type_at_section_indentation():
        docstring = "Summary.\n\n    Returns\n    -------\n        Whether it worked."
        info = parse_docstring_types(docstring)
        rewritten, changed = rewrite_docstring_types(
            docstring,
            info,
            remove_types=False,
            updated_return="bool",
        )
        assert changed is True
        assert (
            "    Returns\n    -------\n    bool\n        Whether it worked."
        ) in rewritten

    @staticmethod
    def test_remove_numpy_types():
        docstring = (
            "Parameters\n"
            "----------\n"
            "name : str\n"
            "    The name.\n\n"
            "Returns\n"
            "-------\n"
            "bool\n"
            "    Whether it worked.\n"
        )
        info = parse_docstring_types(docstring)
        rewritten, changed = rewrite_docstring_types(
            docstring,
            info,
            remove_types=True,
        )
        assert changed is True
        assert "name : str" not in rewritten
        assert "name\n" in rewritten

    @staticmethod
    def test_remove_sphinx_types():
        docstring = ":param str name: The name.\n:rtype: bool\n"
        info = parse_docstring_types(docstring)
        rewritten, changed = rewrite_docstring_types(
            docstring,
            info,
            remove_types=True,
        )
        assert changed is True
        assert ":param name: The name." in rewritten
        assert ":rtype:" not in rewritten


class TestSignatureTypes:
    @staticmethod
    def test_parse_and_build_edits():
        source = textwrap.dedent(
            """
            def foo(name, count=1):
                '''Doc.'''
                return True
            """,
        ).strip()
        tree = ast.parse(source)
        node = tree.body[0]
        signature = parse_signature_types(node)
        assert signature.args == {"name": None, "count": None}
        assert signature.returns is None

        edits = build_signature_edits(
            node,
            source,
            add_args={"name": "str", "count": "int"},
            add_return="bool",
            overwrite_args={},
            overwrite_return=None,
        )
        updated = apply_edits(source, edits)
        assert "name: str" in updated
        assert "count: int" in updated
        assert "-> bool:" in updated

    @staticmethod
    def test_replace_existing_annotations():
        source = "def foo(name: str) -> bool:\n    pass\n"
        node = ast.parse(source).body[0]
        edits = build_signature_edits(
            node,
            source,
            add_args={},
            add_return=None,
            overwrite_args={"name": "int"},
            overwrite_return="str",
        )
        updated = apply_edits(source, edits)
        assert updated == "def foo(name: int) -> str:\n    pass\n"

    @staticmethod
    def test_multiline_signature_return_insert():
        source = "def foo(\n    name,\n):\n    pass\n"
        node = ast.parse(source).body[0]
        edits = build_signature_edits(
            node,
            source,
            add_args={"name": "str"},
            add_return="bool",
            overwrite_args={},
            overwrite_return=None,
        )
        updated = apply_edits(source, edits)
        assert "name: str" in updated
        assert ") -> bool:" in updated

    @staticmethod
    def test_annotation_to_str_for_subscript():
        func = ast.parse("def foo(x: Optional[str]) -> None: ...").body[0]
        assert isinstance(func, ast.FunctionDef)
        assert annotation_to_str(func.args.args[0].annotation) == "Optional[str]"


class TestApplyEdits:
    @staticmethod
    def test_applies_multiple_edits():
        source = "def foo(x, y):\n    pass\n"
        edits = [(1, 8, 1, 9, "x: str"), (1, 11, 1, 12, "y: int")]
        assert apply_edits(source, edits) == "def foo(x: str, y: int):\n    pass\n"

    @staticmethod
    def test_rejects_invalid_line_number():
        with pytest.raises(IndexError):
            apply_edits("x = 1\n", [(99, 0, 99, 1, "y")])


class TestSyncTypeHintsHelpers:
    @staticmethod
    def test_collect_functions_in_classes():
        source = textwrap.dedent(
            """
            class Example:
                def method(self):
                    pass
            """,
        ).strip()
        tree = ast.parse(source)
        functions = _collect_functions(tree)
        assert len(functions) == 1
        assert functions[0].qualified_name == "Example.method"

    @staticmethod
    def test_get_docstring_node():
        source = 'def foo():\n    """Doc."""\n    pass\n'
        node = ast.parse(source).body[0]
        docstring = _get_docstring_node(node)
        assert docstring is not None
        assert docstring[1] == "Doc."

    @staticmethod
    def test_plan_function_edits_prefers_docstring(tmp_path):
        source = textwrap.dedent(
            """
            def foo(name: int) -> bool:
                '''Summary.

                Args:
                    name (str): The name.
                '''
                return True
            """,
        ).strip()
        file = tmp_path / "example.py"
        tree = ast.parse(source)
        context = _collect_functions(tree)[0]
        edits, changed = _plan_function_edits(
            source,
            context,
            file,
            HookConfig(on_clash="prefer-docstring"),
        )
        assert changed is True
        updated = apply_edits(source, edits)
        assert "name: str" in updated

    @staticmethod
    def test_plan_function_raises_on_clash(tmp_path):
        source = textwrap.dedent(
            """
            def foo(name: int):
                '''Summary.

                Args:
                    name (str): The name.
                '''
                return True
            """,
        ).strip()
        file = tmp_path / "example.py"
        tree = ast.parse(source)
        context = _collect_functions(tree)[0]
        with pytest.raises(TypeClashError):
            _plan_function_edits(
                source,
                context,
                file,
                HookConfig(on_clash="error"),
            )

    @staticmethod
    def test_plan_function_adds_signature_types_to_docstring(tmp_path):
        source = textwrap.dedent(
            '''
            def foo(name: str) -> bool:
                """Summary.

                Args:
                    name: The name.

                Returns:
                    Whether it worked.
                """
                return True
            ''',
        ).strip()
        file = tmp_path / "example.py"
        context = _collect_functions(ast.parse(source))[0]

        edits, changed = _plan_function_edits(source, context, file, HookConfig())

        assert changed is True
        updated = apply_edits(source, edits)
        assert "name (str): The name." in updated
        assert "bool: Whether it worked." in updated

    @staticmethod
    def test_plan_function_preserves_indented_numpy_return_type(tmp_path):
        source = textwrap.dedent(
            '''
            def select_active_space() -> ActiveSpaceSelectionResult:
                """Select an active space.

                Returns
                -------
                ActiveSpaceSelectionResult
                    Uniform descriptive result.
                """
            ''',
        ).strip()
        file = tmp_path / "example.py"
        context = _collect_functions(ast.parse(source))[0]

        edits, changed = _plan_function_edits(source, context, file, HookConfig())

        assert changed is False
        assert edits == []

    @staticmethod
    def test_signature_only_moves_docstring_types_to_signature(tmp_path):
        source = textwrap.dedent(
            '''
            def foo(name):
                """Args:
                    name (str): The name.
                """
                return name
            ''',
        ).strip()
        file = tmp_path / "example.py"
        context = _collect_functions(ast.parse(source))[0]

        edits, changed = _plan_function_edits(
            source,
            context,
            file,
            HookConfig(signature_types_only=True),
        )

        assert changed is True
        updated = apply_edits(source, edits)
        assert "def foo(name: str):" in updated
        assert "name: The name." in updated
        assert "name (str)" not in updated

    @staticmethod
    def test_sync_type_hints_syntax_error(tmp_path, capsys):
        file = tmp_path / "broken.py"
        file.write_text("def broken(:\n")
        assert _sync_type_hints(file, HookConfig()) == 1
        captured = capsys.readouterr()
        assert "could not parse file" in captured.err

    @staticmethod
    def test_sync_type_hints_ignore_pragma(tmp_path):
        source = textwrap.dedent(
            """
            def foo(name):  # pragma: no sync-type-hints
                '''Args:
                    name (str): The name.
                '''
                return name
            """,
        ).strip()
        file = tmp_path / "ignored.py"
        file.write_text(source)
        assert _sync_type_hints(file, HookConfig()) == 0

    @staticmethod
    def test_load_config_without_file(monkeypatch):
        monkeypatch.chdir("/tmp")
        assert _load_config() == HookConfig()

    @staticmethod
    def test_load_config_from_pyproject(tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "pyproject.toml").write_text(
            "[tool.sync_type_hints]\n"
            'on-clash = "prefer-signature"\n'
            "signature-types-only = true\n",
        )
        config = _load_config()
        assert config.on_clash == "prefer-signature"
        assert config.signature_types_only is True

    @staticmethod
    def test_load_signature_types_only_underscore_key(tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "pyproject.toml").write_text(
            "[tool.sync_type_hints]\nsignature_types_only = true\n",
        )
        assert _load_config().signature_types_only is True


class TestTypeClashError:
    @staticmethod
    def test_message():
        error = TypeClashError("file.py", "foo", "x", "str", "int")
        assert "docstring has 'str'" in str(error)
        assert "signature has 'int'" in str(error)
