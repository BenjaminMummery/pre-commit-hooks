import argparse
from typing import List, Tuple


def _construct_file_lists(
    filenames: List[str],
) -> Tuple[List[str], List[str], List[str]]:
    if len(filenames) == 0:
        return [], [], []
    if filenames[0].startswith("src"):
        return filenames, [], []
    return [], filenames, []


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*")
    args = parser.parse_args(argv)

    if len(args.filenames) > 0:
        return 1
    return 0
