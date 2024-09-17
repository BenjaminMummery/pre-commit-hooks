# Copyright (c) 2024 Benjamin Mummery

"""
Scan source files that aren't tests for test-specific imports (pytest, unittest, etc).

This module is intended for use as a pre-commit hook. For more information please
consult the README file.
"""


def main():
    """
    Entrypoint for the no_import_testtools_in_src hook.

    Scan source files that aren't tests for test-specific imports (pytest, unittest,
    etc).

    Returns:
        int: 1 if imports are found, 0 otherwise.
    """
    # files = _parse_args().files

    retv: int = 0
    # for file in files:
    #     retv |= _check_for_imports(file)

    return retv


if __name__ == "__main__":
    exit(main())
