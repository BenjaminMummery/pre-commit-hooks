# Copyright (c) 2023-2026 Benjamin Mummery

"""
Module docstring.
===============
"""

CONST = 3
"""
Const docstring.
==============
"""


def main():
    """
    Function docstring.
    ================
    """


class foo:
    """
    Class docstring.
    ==============
    """

    def method():
        """
        Method docstring.
        ============
        """

    class NestedClass:
        """
        Nested CLass docstring.
        ==============
        """


        def nested_method():
            """
            Nested Method docstring.
            =================
            """


expected_stdout: str = """- error in module docstring: Title underline too short.
- error in docstring of function 'main' (lineno 15): Title underline too short.
- error in docstring of class 'foo' (lineno 23): Title underline too short.
- error in docstring of method 'method' of class 'foo' (lineno 29): Title underline too short.
- error in docstring of class 'NestedClass' (lineno 36): Title underline too short.
- error in docstring of method 'nested_method' of class 'NestedClass' (lineno 44): Title underline too short.
"""  # noqa: E501
