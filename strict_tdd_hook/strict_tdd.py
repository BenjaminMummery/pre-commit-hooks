import argparse


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*")
    args = parser.parse_args(argv)

    if len(args.filenames) > 0:
        return 1
    return 0
