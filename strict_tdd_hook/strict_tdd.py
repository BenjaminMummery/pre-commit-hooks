import argparse
from typing import List, Tuple


def _parse_file_list(
    filenames: List[str],
) -> Tuple[List[str], List[str], List[str]]:
    """
    Parse the list of files into lists of source files, test files, and other

    Args:
        filenames (List[str]): The list of changed files.

    Returns:
        source files, test files, other files: Lists of the filenames corresponding to
            each category.
    """
    source_files: List[str] = []
    test_files: List[str] = []
    etc_files: List[str] = []

    for file in filenames:
        if file.startswith("src"):
            source_files.append(file)
        elif file.startswith("test"):
            test_files.append(file)
        else:
            etc_files.append(file)

    return source_files, test_files, etc_files


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*")
    args = parser.parse_args(argv)

    if len(args.filenames) > 0:
        return 1
    return 0
