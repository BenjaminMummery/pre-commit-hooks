# Copyright (c) 2023 Benjamin Mummery

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
    pass


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
        pass

    class NestedClass:
        """
        Nested CLass docstring.
        ==============
        """

        pass

        def nested_method():
            """
            Nested Method docstring.
            =================
            """
            pass


expected_stdout: str = """- error in module docstring: Title underline too short.
- error in docstring of function 'main' (lineno 15): Title underline too short.
- error in docstring of class 'foo' (lineno 23): Title underline too short.
- error in docstring of method 'method' of class 'foo' (lineno 29): Title underline too short.
- error in docstring of class 'NestedClass' (lineno 36): Title underline too short.
- error in docstring of method 'nested_method' of class 'NestedClass' (lineno 44): Title underline too short.
"""  # noqa: E501
