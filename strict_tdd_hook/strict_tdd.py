import argparse
from typing import List, Tuple


def _construct_file_lists(
    filenames: List[str],
) -> Tuple[List[str], List[str], List[str]]:
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
